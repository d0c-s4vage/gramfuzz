# gramfuzz

[![Master Build Status](https://travis-ci.org/d0c-s4vage/gramfuzz.svg?branch=master)](https://travis-ci.org/d0c-s4vage/gramfuzz)
[![PyPI Statistics](https://img.shields.io/pypi/dm/gramfuzz)](https://pypistats.org/packages/gramfuzz)
[![Latest Release](https://img.shields.io/pypi/v/gramfuzz)](https://pypi.python.org/pypi/gramfuzz/)

`gramfuzz` is a grammar-based fuzzer that lets one define
complex grammars to model text and binary data formats.

- [Contributing](#contributing)
- [Installation](#installation)
- [Documentation](#documentation)
- [TLDR Example](#tldr-example)
- [More Examples](#more-examples)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details. PRs welcome!

## Installation

Install via pip:

```
pip install gramfuzz
```

## Documentation

For detailed documentation, please [view the full docs here](https://d0c-s4vage.github.io/gramfuzz/)

## TLDR Example


Suppose we define a grammar for generating names and their prefixes
and suffixes:

```python
# names_grammar.py
import gramfuzz
from gramfuzz.fields import *

class NRef(Ref):
    cat = "name_def"
class NDef(Def):
    cat = "name_def"


Def("name",
    Opt(NRef("name_title")),
    NRef("personal_part"),
    NRef("last_name"),
    Opt(NRef("name_suffix")),
cat="name", sep=" ")
NDef("personal_part",
    NRef("initial") | NRef("first_name"), Opt(NRef("personal_part")),
sep=" ")
NDef("last_name", Or(
    "Blart", "Tralb"
))
NDef("name_suffix",
    Opt(NRef("seniority")),
    Or("Phd.", "CISSP", "MD.", "MBA", "NBA", "NFL", "WTF", "The Great"),
sep=" ")
NDef("seniority", Or("Sr.", "Jr."))
NDef("name_title", Or(
    "Sir", "Ms.", "Mr.", "Mrs.", "Senator", "Capt.", "Maj.", "Lt.", "President"
))
NDef("first_name", Or("Henry", "Susy"))
NDef("initial",
    String(min=1, max=2, charset=String.charset_alpha_upper), "."
)
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
Ms. Susy Henry Tralb
Lt. Henry Henry Tralb
L. Tralb WTF
Maj. L. W. N. Tralb
Z. Tralb
Senator C. K. Henry Blart
Henry Tralb CISSP
Lt. Henry Tralb Jr. NBA
Maj. Susy Tralb Sr. NBA
Henry C. Blart WTF
```

## More Examples

See the examples (and example script) in the examples folder:

```
 lptp [ tmp ]: git clone https://github.com/d0c-s4vage/gramfuzz
 lptp [ tmp ]: cd gramfuzz/examples
 lptp [ examples ]: ./example.py --help
usage: gramfuzz/examples/example.py [-h] -g GRAMMAR [-n N] [-s RAND_SEED]
                                    [--max-recursion R] [-o OUTPUT]

This script will generate N instances of the specified grammar.

optional arguments:
  -h, --help            show this help message and exit
  -g GRAMMAR, --grammar GRAMMAR
                        The grammar to load. One of: names,python27,roman_numeral,postal
  -n N, --number N      The number of times to generate top-level nodes from the specified grammar(s) (default=1)
  -s RAND_SEED, --seed RAND_SEED
                        The random seed to initialize the PRNG with (default=None)
  --max-recursion R     The maximum reference recursion depth allowed (default=10)
  -o OUTPUT, --output OUTPUT
                        The output file to output the generated data to (default=stdout)
 lptp [ examples ]: ./example.py -g postal -n 10 -s 1337 --max-recursion 5
Z. Tralb
69 Baker Street 8325U 
Malang, IL 64666-4973
Senator Susy Henry Blart WTF
56 Sesame Street 
Yokohama, WV 49471-3667
Henry I. Tralb Jr. CISSP
63 Spooner Street 858H 
Tehran, TX 27259-9556
Capt. Henry Susy Blart Jr. Phd.
65536 Jump Street 
Malang, ID 84108-0969
Susy Blart
0 Rainey Street 
Wuhan, FL 16712-1095
P. Blart NFL
98 Wisteria Lane 
Shenyang, NH 70126
Henry Henry Blart Phd.
30 Rainey Street 
Madras, GA 90915
Senator Henry E. Tralb
38 Spooner Street 
Tianjin, CT 37211
Maj. Henry Tralb
70 Rainey Street 458W 
HongKong, OK 40689
Mrs. Henry Blart
11 Sesame Street 
Beijing, MT 58689-7258
```

## Contributors

* @docfate111
