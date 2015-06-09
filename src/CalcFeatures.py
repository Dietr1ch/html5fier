#!/usr/bin/python3

import sys
import ujson

from tags import SEMANTIC_TAGS

import ElemFeatures
from ElemFeatures import site, site_stats, site_visible_elements, features

driver = ElemFeatures.get_driver()

divTags = SEMANTIC_TAGS.union({"div"})


i = 0
for url in sys.stdin:
    i += 1
    try:
        print("\n")  # 2 lines
        print("%4d: %s" % (i, url.strip()))
        url = site(url)
        site_stats()

        # Too slow
        if False or True:
            # 1. Calculate Features
            elems = site_visible_elements()
            print("Calculating features...")
            feats = features(elems)
            print("Done")

            # 2. Count semantic tag usage
            tag_elems = {}
            for t in divTags:
                tag_elems[t] = ElemFeatures.site_body_tag(t)

            # 3. Show features
            print("Features for 'div tags'")

            divs = 0
            for f in feats:
                elemJSON = ujson.dumps(f)
                if f.Tag == "div":
                    divs += 1
                elif f.Tag in SEMANTIC_TAGS:
                    print("  {}".format(elemJSON))

            print("  + {} div tags".format(divs))

    except Exception as e:
        print("Failed to get '{}' ({})\n".format(site, e))
