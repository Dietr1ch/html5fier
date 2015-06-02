#!/usr/bin/python3

import sys
import re
import ujson
from selenium import webdriver

w = 1024
h = 768

# Set up Chromium
driver = webdriver.Chrome()
menuHeight = 61
driver.set_window_size(w, h+menuHeight)

siteRegex = re.compile(r'^https?://')


def getElems(url):
    driver.get(url)
    return driver.find_elements_by_xpath("//*")


def getBodyElems(url):
    driver.get(url)
    return driver.find_elements_by_xpath("/html/body//*")


def getVisibleElems(url):
    if siteRegex.match(url) is None:
        site = "http://{}".format(url)
    else:
        site = url

    print("Navigating to '{}'...".format(site))
    elems = getBodyElems(site)
    return [e for e in elems if e.is_displayed()]


def getLinkTarget(elem):
    t = elem.get_attribute("href")

    if t is None:
        return None
    else:
        # TODO: check relative or same site link
        return None


def getChildren(elem):
    return elem.find_elements_by_xpath(".//*")


class ElemFeatures():
    _element = None  # Selenium element
    _children = []  # Selenium element

    Tag = ""

    # Element features
    # ----------------

    # Element size and location
    s_x = -1  # Width
    s_y = -1  # Height
    s_a = -1  # Area

    l_x = -1  # X
    l_y = -1  # Y

    # Location if visible
    losiv_x = -1  # X
    losiv_y = -1  # Y

    # Element text data
    textSize = -1
    textWords = -1

    # Pending Features
    # ================

    # Children data
    _children_count = 0
    _children_normalized_histogram = []

    # Links
    # -----
    # Links inside tree
    _links_tree_relative = 0
    _links_tree_same_site = 0
    _links_tree_external = 0
    # Direct children links
    _links_children_relative = 0
    _links_children_same_site = 0
    _links_children_external = 0

    # Style
    # -----
    _font_size_px = -1
    _font_bold = None  # None, False, True
    _font_italic = None
    _font_color = None

    def __init__(self, elem):
        # Set up
        self._element = elem
        self._children = getChildren(elem)

        # Calculate features
        self.getFeatures()
        self.getTagName()
        self.getText()
        pass

    def getFeatures(self):
        s = self._element.size
        self.s_x = s['width']
        self.s_y = s['height']
        self.s_a = self.s_x * self.s_y

        l = self._element.location
        self.l_x = l['x']
        self.l_y = l['y']

        l = self._element.location_once_scrolled_into_view
        self.losiv_x = l['x']
        self.losiv_y = l['y']
        pass

    def getTagName(self):
        self.Tag = self._element.tag_name
        pass

    def getText(self):
        self.textSize = len(self._element.text)
        self.textWords = len(self._element.text.split())
        pass


def main():
    for site in sys.stdin:
        try:
            site = site.strip()

            elems = getVisibleElems(site)
            features = [ElemFeatures(e) for e in elems]

            j = ujson.dumps(
                {
                    'site': site,
                    'elements': features,
                })
            print("{}, {}\n".format(site, j))

        except Exception as e:
            print("Failed to get '{}' ({})\n".format(site, e))


if __name__ == '__main__':
    main()
