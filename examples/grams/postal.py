#!/usr/bin/env python
# -*- coding: utf-8 -*-


from gramfuzz.fields import *

import names


TOP_CAT = "postal"


# Adapted from  https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form
# The name rules have been modified and placed into names.py


class PDef(Def):
    cat = "postal_def"
class PRef(Ref):
    cat = "postal_def"


EOL = "\n"


# this will be the top-most rule
Def("postal_address",
    PRef("name-part"), PRef("street-address"), PRef("zip-part"),
cat="postal")

# these will be the grammar rules that should not be randomly generated
# as a top-level rule
PDef("name-part", 
    Ref("name", cat=names.TOP_CAT), EOL
)
PDef("street-address",
    PRef("house-num"), PRef("street-name"), Opt(PRef("apt-num")), EOL,
sep=" ")
PDef("house-num", UInt)
PDef("street-name", Or(
    "Sesame Street", "Yellow Brick Road", "Jump Street", "Evergreen Terrace",
    "Elm Street", "Baker Street", "Paper Street", "Wisteria Lane",
    "Coronation Street", "Rainey Street", "Spooner Street",
    "0day Causeway", "Diagon Alley",
))
PDef("zip-part",
    PRef("town-name"), ", ", PRef("state-code"), " ", PRef("zip-code"), EOL
)
PDef("apt-num",
    UInt(min=0, max=10000), Opt(String(charset=String.charset_alpha_upper, min=1, max=2))
)
PDef("town-name", Or(
    "Seoul", "São Paulo", "Bombay", "Jakarta", "Karachi", "Moscow",
    "Istanbul", "Mexico City", "Shanghai", "Tokyo", "New York", "Bangkok",
    "Beijing", "Delhi", "London", "HongKong", "Cairo", "Tehran", "Bogota",
    "Bandung", "Tianjin", "Lima", "Rio de Janeiro" "Lahore", "Bogor",
    "Santiago", "St Petersburg", "Shenyang", "Calcutta", "Wuhan", "Sydney",
    "Guangzhou", "Singapore", "Madras", "Baghdad", "Pusan", "Los Angeles",
    "Yokohama", "Dhaka", "Berlin", "Alexandria", "Bangalore", "Malang",
    "Hyderabad", "Chongqing", "Ho Chi Minh City",
))
PDef("state-code", Or(
    "AL", "AK", "AS", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA",
    "GU", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MH",
    "MA", "MI", "FM", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM",
    "NY", "NC", "ND", "MP", "OH", "OK", "OR", "PW", "PA", "PR", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "VI", "WA", "WV", "WI", "WY",
))
PDef("zip-code",
    String(charset="123456789",min=1,max=2), String(charset="0123456789",min=4,max=5),
    Opt("-", String(charset="0123456789",min=4,max=5))
)
