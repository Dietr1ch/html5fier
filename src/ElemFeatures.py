#!/usr/bin/python3

import re

siteRegex = re.compile(r'https?://')


def site_elements(driver, url):
    driver.get(url)
    return driver.find_elements_by_xpath("//*")


def site_body_elements(driver, url):
    driver.get(url)
    return driver.find_elements_by_xpath("/html/body//*")


def site_visible_elements(url):
    if siteRegex.match(url) is None:
        site = "http://{}".format(url)
    else:
        site = url

    print("Navigating to '{}'...".format(site))
    elems = site_body_elements(site)
    return [e for e in elems if e.is_displayed()]


def elem_attr(elem, attr):
    return elem.get_attribute(attr)


def elem_link_target(elem):
    return elem.get_attribute("href")


def elem_id(elem):
    return elem.get_attribute("id")


def elem_title(elem):
    return elem.get_attribute("title")


def children(elem):
    return elem.find_elements_by_xpath("./*")


def descendants(elem):
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
        self._children = children(elem)

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
