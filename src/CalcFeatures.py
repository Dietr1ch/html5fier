#!/usr/bin/python3

import sys
import ujson

from tags import SEMANTIC_TAGS

import ElemFeatures
from ElemFeatures import site

driver = ElemFeatures.get_driver()

divTags = SEMANTIC_TAGS.union({"div"})

for url in sys.stdin:
    try:
        site(url)
        elems = ElemFeatures.site_visible_elements()
        features = [ElemFeatures(e) for e in elems]

        j = {}
        for t in divTags:
            j[t] = ElemFeatures.site_body_tag(t)

        j = ujson.dumps(
            {
                'site': site,
                'elements': features,
            })
        print("{}, {}\n".format(site, j))

    except Exception as e:
        print("Failed to get '{}' ({})\n".format(site, e))
