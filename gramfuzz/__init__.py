#!/usr/bin/env python
# encoding: utf-8


"""
This module defines the main ``GramFuzzer`` class through
which rules are defined and rules are randomly generated.
"""


from collections import deque
import copy
import gc
import os
import sys


import gramfuzz.errors as errors
import gramfuzz.rand as rand
import gramfuzz.utils as utils


class GramFuzzer(object):
    """
    ``GramFuzzer`` is a singleton class that is used to
    hold rule definitions and to generate grammar rules from a specific
    category at random.
    """

    defs = {}
    """Rule definitions by category. E.g. ::
        
        {
            "category": {
                "rule1": [<Rule1Def1>, <Rule1Def2>],
                "rule2": [<Rule2Def1>, <Rule2Def2>],
                ...
            }
        }
    """

    no_prunes = {}
    """Rules that have specifically asked not to be pruned,
    even if the rule can't be reached.
    """

    cat_groups = {}
    """Used to store where rules were defined in. E.g. if a rule
    ``A`` was defined using the category ``alphabet_rules`` in a file
    called ``test_rules.py``, it would show up
    in ``cat_groups`` as: ::

        {
            "alphabet_rules": {
                "test_rules": ["A"]
            }
        }

    This lets the user specify probabilities/priorities for rules coming
    from certain grammar files
    """

    __instance__ = None
    @classmethod
    def instance(cls):
        """Return the singleton instance of the ``GramFuzzer``
        """
        if cls.__instance__ is None:
            cls()
        return cls.__instance__


    def __init__(self):
        """Create a new ``GramFuzzer`` instance
        """
        GramFuzzer.__instance__ = self
        self.defs = {}
        self.no_prunes = {}
        self.cat_groups = {}

        # used during rule generation to keep track of things
        # that can be reverted if things go wrong
        self._staged_defs = None

        # the last-defined preferred category-group names
        self._last_prefs = None

        # the last-defined rule definition names derived from the ``_last_prefs``
        self._last_pref_keys = None
    
    def load_grammar(self, path):
        """Load a grammar file (python file containing grammar definitions) by
        file path. When loaded, the global variable ``GRAMFUZZER`` will be set
        within the module. This is not always needed, but can be useful.

        :param str path: The path to the grammar file
        """
        if not os.path.exists(path):
            raise Exception("path does not exist: {!r}".format(path))

        with open(path, "r") as f:
            data = f.read()
            code = compile(data, path, "exec")

        exec code in {"GRAMFUZZER": self}
    
    def prune(self, check_cats, target_cat):
        """Iterate over every rule defined in every category in ``check_cats``
        to see if each rule can be reached from a rule defined in ``target_cat``.

        If a rule defined in ``check_cats`` cannot be reached from a rule in ``target_cat``
        and the rule has not explicitly asked to not be pruned, the rule will be
        removed from memory.
        """
        if target_cat not in self.defs:
            return

        # iterate over the rules until we cannot prune anymore
        to_delete = {}
        while True:
            prev_length = self._get_to_del_length(to_delete)

            # check each rule in each category in check_cats
            for check_cat in check_cats:
                for check_name,check_vals in self.defs[check_cat].iteritems():
                    for check_val in check_vals:
                        
                        # if this specific rule cannot be reached from any rule
                        # defined in ``target_cat``, prune it
                        self.prune_if_unreachable_from(
                            rule_cat  = check_cat,
                            rule_name = check_name,
                            rule_val  = check_val,
                            from_cat  = target_cat,
                            to_delete = to_delete
                        )
            
            # we found nothing else to prune, so break
            if prev_length == self._get_to_del_length(to_delete):
                break

        # delete every rule queued for deletion
        for del_cat,del_info in to_delete.iteritems():
            for del_name,del_vals in del_info.iteritems():
                if del_cat not in self.defs:
                    break
                if del_name not in self.defs[del_cat]:
                    break

                for del_val in del_vals:
                    vals = self.defs[del_cat][del_name]
                    if del_val in vals:
                        vals.remove(del_val)
                    if len(vals) == 0:
                        del self.defs[del_cat][del_name]
    
    def prune_if_unreachable_from(self, rule_cat, rule_name, rule_val, from_cat, to_delete):
        """Prune a rule if it cannot be reached by any rule in ``from_cat``

        :param str rule_cat: The category of the rule
        :param str rule_name: The name of the rule
        :param rule_val: The value of the rule
        :param str from_cat: The category to check if the rule is reachable from
        :param list to_delete: The collection to add the rule to if it should be pruned
        """
        # collect all Refs contained within the rule_val
        all_refs = self._collect_refs(rule_val)

        # the rule will be pruned if one or more referenced rules in ``rule_val`` cannot
        # be reached from a rule in ``from_cat``
        for ref in all_refs:
            if ref.refname not in self.defs[from_cat]:# or (from_cat in to_delete and ref.refname in to_delete[from_cat]):
                to_delete.setdefault(rule_cat, {}).setdefault(rule_name, set()).add(rule_val)
                break

        return all_refs
    
    def _get_to_del_length(self, to_delete):
        length = 0
        for cat,names in to_delete.iteritems():
            for name,vals in names.iteritems():
                length += len(vals)
        return length
    
    def _collect_refs(self, item_val, acc=None):
        if acc is None:
            acc = deque()

        from gramfuzz.fields import Ref
        if isinstance(item_val, Ref):
            acc.append(item_val)

        if hasattr(item_val, "values"):
            for val in item_val.values:
                self._collect_refs(val, acc)

        return acc
    
    # --------------------------------------
    # public, but intended for internal use
    # --------------------------------------
    
    def add_definition(self, cat, def_name, def_val, no_prune=False, gram_file="default"):
        """Add a new rule definition named ``def_name`` having value ``def_value`` to
        the category ``cat``.

        :param str cat: The category to add the rule to
        :param str def_name: The name of the rule definition
        :param def_val: The value of the rule definition
        :param bool no_prune: If the rule should explicitly *NOT*
            be pruned even if it has been determined to be unreachable (default=``False``)
        :param str gram_file: The file the rule was defined in (default=``"default"``).
        """
        self.add_to_cat_group(cat, gram_file, def_name)

        if no_prune:
            self.no_prunes.setdefault(cat, {}).setdefault(def_name, True)

        if self._staged_defs is not None:
            # if we're tracking changes during rule generation, add any new rules
            # to _staged_defs so they can be reverted if something goes wrong
            self._staged_defs.append((cat, def_name, def_val))
        else:
            self.defs.setdefault(cat, {}).setdefault(def_name, deque()).append(def_val)
    
    def add_to_cat_group(self, cat, cat_group, def_name):
        """Associate the provided rule definition name ``def_name`` with the
        category group ``cat_group`` in the category ``cat``.

        :param str cat: The category the rule definition was declared in
        :param str cat_group: The group within the category the rule belongs to
        :param str def_name: The name of the rule definition
        """
        self.cat_groups.setdefault(cat, {}).setdefault(cat_group, deque()).append(def_name)
    
    def get_ref(self, cat, refname):
        """Return one of the rules in the category ``cat`` with the name
        ``refname``. If multiple rule defintions exist for the defintion name
        ``refname``, use :any:`gramfuzz.rand` to choose a rule at random.

        :param str cat: The category to look for the rule in.
        :param str refname: The name of the rule definition. If the rule definition's name is
            ``"*"``, then a rule name will be chosen at random from within the category ``cat``.
        :returns: gramfuzz.fields.Def
        """
        if cat not in self.defs:
            raise errors.GramFuzzError("referenced definition category ({!r}) not defined".format(cat))
        
        if refname == "*":
            refname = rand.choice(self.defs[cat].keys())
            
        if refname not in self.defs[cat]:
            raise errors.GramFuzzError("referenced definition ({!r}) not defined".format(refname))

        return rand.choice(self.defs[cat][refname])


    def gen(self, cat, num, preferred=None, preferred_ratio=0.5):
        """Generate ``num`` rules from category ``cat``, optionally specifying
        preferred category groups ``preferred`` that should be preferred at
        probability ``preferred_ratio`` over other randomly-chosen rule definitions.

        :param str cat: The name of the category to generate ``num`` rules from
        :param int num: The number of rules to generate
        :param list preferred: A list of preferred category groups to generate rules from
        :param float preferred_ratio: The percent probability that the preferred
        groups will be chosen over randomly choosen rule definitions from category ``cat``.
        """
        if preferred is None:
            preferred = []

        res = deque()
        cat_defs = self.defs[cat]

        # optimizations
        _res_append = res.append
        _res_extend = res.extend
        _choice = rand.choice
        _maybe = rand.maybe
        _val = utils.val

        keys = self.defs[cat].keys()

        self._last_pref_keys = self._get_pref_keys(cat, preferred)
        # be sure to set this *after* fetching the pref keys (above^)
        self._last_prefs = preferred

        total_errors = deque()
        total_gend = 0
        while total_gend < num:
            # use a rule definition from one of the preferred category
            # groups
            if len(self._last_pref_keys) > 0 and _maybe(preferred_ratio):
                rand_key = _choice(self._last_pref_keys)
                if rand_key not in cat_defs:
                    # TODO this means it was removed / pruned b/c it was unreachable??
                    # TODO look into this more
                    rand_key = _choice(keys)

            # else just choose a key at random from the category
            else:
                rand_key = _choice(keys)

            # pruning failed, this rule is not defined/reachable
            if rand_key not in cat_defs:
                continue

            v = _choice(cat_defs[rand_key])

            # not used directly by GramFuzzer, but could be useful
            # to subclasses of GramFuzzer
            info = {}

            pre = deque()
            self.pre_revert(info)
            val_res = None

            try:
                val_res = _val(v, pre)
            except errors.GramFuzzError as e:
                total_errors.append(e)
                self.revert(info)
                continue
            except RuntimeError as e:
                self.revert(info)
                continue

            if val_res is not None:
                _res_extend(pre)
                _res_append(val_res)

                total_gend += 1
                self.post_revert(cat, res, total_gend, num, info)

        return res
    
    def pre_revert(self, info=None):
        """Signal to begin saving any changes that might need to be reverted
        """
        self._staged_defs = deque()
    
    def post_revert(self, cat, res, total_num, num, info):
        """Commit any staged rule definition changes (rule generation went
        smoothly).
        """
        if self._staged_defs is None:
            return
        for cat,def_name,def_value in self._staged_defs:
            self.defs.setdefault(cat, {}).setdefault(def_name, deque()).append(def_value)
        self._staged_defs = None
    
    def revert(self):
        """Revert after a single def errored during generate (throw away all
        staged rule definition changes)
        """
        self._staged_defs = None

    def _get_pref_keys(self, cat, preferred):
        if preferred == self._last_prefs:
            pref_keys = self._last_pref_keys
        else:
            pref_keys = deque()
            for pref in preferred:
                if pref in self.cat_groups[cat]:
                    pref_keys.extend(self.cat_groups[cat][pref])
                elif pref in self.defs[cat]:
                    pref_keys.append(pref)

        return pref_keys
