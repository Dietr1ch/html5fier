#!/usr/bin/python3

import sys
import ujson

from tags import SEMANTIC_TAGS

import ElemFeatures
from ElemFeatures import site, site_stats, site_visible_elements, features, FeatureTree

driver = ElemFeatures.get_driver()

divTags = [t for t in SEMANTIC_TAGS].append("div")


feature_labels = None

i = 0
for url in sys.stdin:
    i += 1
    try:
        print("##### %4d: %s" % (i, url.strip()))
        url = site(url)
        semantic_tag_count = site_stats()

        with open("site-list.txt", "a") as f:
            f.write("{},{}\n".format(semantic_tag_count, url))

        # Too slow
        if semantic_tag_count < 5:
            print("# Site has only {} semantic tag samples. Skipping..."
                  .format(semantic_tag_count))
            continue

        # continue

        # 1. Calculate Features
        #print("Getting visible elements...")
        #elems = site_visible_elements()
        print("# Calculating features...")
        feats = FeatureTree(driver)
        #feats = features(elems)
        print("# Done calculating features")

        # 3. Print features

        for node in feats:
            if node.use:
                if not feature_labels:
                    feature_labels = node.features.keys()
                    print('url,tag,{}'.format(','.join(feature_labels)))

                feature_list = []
                for feat_name in feature_labels:
                    feature_list.append(node.get_feature(feat_name))

                tag = node.element.tag_name.lower()
                values = [url, tag] + feature_list
                print(','.join(map(str, values)))

    except Exception as e:
        print("# Failed to get '{}' ({})\n".format(url, e))

driver.close()
