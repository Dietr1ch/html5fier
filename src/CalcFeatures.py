#!/usr/bin/python3

import sys
import ujson
from selenium import webdriver

import ElemFeatures

# Set up Chromium
driver = webdriver.Chrome()
w = 1024
h = 768
menuHeight = 61
driver.set_window_size(w, h+menuHeight)

for site in sys.stdin:
    try:
        site = site.strip()
        elems = ElemFeatures.site_visible_elements(site)
        features = [ElemFeatures(e) for e in elems]

        j = ujson.dumps(
            {
                'site': site,
                'elements': features,
            })
        print("{}, {}\n".format(site, j))

    except Exception as e:
        print("Failed to get '{}' ({})\n".format(site, e))
