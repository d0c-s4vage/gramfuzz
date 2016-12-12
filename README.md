# gramfuzz

[![Build Status: Master](https://travis-ci.org/d0c-s4vage/gramfuzz.svg?branch=master)](https://travis-ci.org/d0c-s4vage/gramfuzz)
[![Build Status: Develop](https://travis-ci.org/d0c-s4vage/gramfuzz.svg?branch=develop)](https://travis-ci.org/d0c-s4vage/gramfuzz)

`gramfuzz` is a grammar-based fuzzer that lets one define
complex grammars to model text and binary data formats.

## Documentation

For detailed documentation, please [view the full docs here](https://d0c-s4vage.github.io/gramfuzz/)

## TLDR Example


Suppose we define a grammar for generating names and their prefixes
and suffixes:

```python
# names_grammar.py
from gramfuzz.fields import *

class NRef(Ref):
	cat = "name_def"
class NDef(Def):
	cat = "name_def"

Def("name",
	Join(
		Opt(NRef("name_prefix")),
		NRef("first_name"),
		Opt(NRef("middle_initial")),
		Opt(NRef("last_name")),
		Opt(NRef("name_suffix")),
	sep=" "),
	cat="name"
)
NDef("name_prefix", Or("Sir", "Ms", "Mr"))
NDef("first_name", Or("Henry", "Susy"))
NDef("middle_initial", String(min=1, max=2), ".")
NDef("last_name", Or("Blart", "Tralb"))
NDef("name_suffix", Or("Phd.", "II", "III"))
```

We could then use this grammar like so:

```python
import gramfuzz

fuzzer = gramfuzz.GramFuzzer()
fuzzer.load_grammar("names_grammar.py")
names = fuzzer.gen(cat="name", num=10)
print("\n".join(names))
```

Which would output something like this:

```
Susy
Henry Blart
Susy J. Tralb Phd.
Ms Susy p. Tralb Phd.
Henry Blart II
Henry T. Blart
Sir Susy D.
Ms Henry Blart II
Susy Z. Phd.
Susy Tralb
```