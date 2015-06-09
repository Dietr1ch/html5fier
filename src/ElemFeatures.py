#!/usr/bin/python3

import re

from tags import SEMANTIC_TAGS

import contextlib
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of

siteRegex = re.compile(r'https?://')

global dri
dri = None


def get_driver(driver=None):
    global dri
    if driver is not None:
        return driver
    if dri is not None:
        return dri
    from selenium import webdriver

    # Set up Chromium
    dri = webdriver.Chrome()
    w = 1024
    h = 768
    menuHeight = 61
    dri.set_window_size(w, h+menuHeight)

    return dri


def site(url="github.com", driver=None):
    driver = get_driver(driver)

    url = url.strip()
    if siteRegex.match(url) is None:
        url = "http://{}".format(url)

    print("Navigating to '{}'...".format(url))
    driver.get(url)
    wait_for_page_load(driver)
    print("Done")

    return url


@contextlib.contextmanager
def wait_for_page_load(driver, timeout=30):
    old_page = driver.find_element_by_tag_name('html')
    yield
    WebDriverWait(driver, timeout).until(staleness_of(old_page))


def site_elements(driver=None):
    driver = get_driver(driver)
    return driver.find_elements_by_xpath("//*")


def site_body_elements(driver=None):
    driver = get_driver(driver)
    return driver.find_elements_by_xpath("/html/body//*")


def site_body_tag(tag, driver=None):
    driver = get_driver(driver)
    return driver.find_elements_by_xpath("/html/body//{}".format(tag))


def site_visible_elements(driver=None):
    driver = get_driver(driver)

    elems = site_body_elements(driver)
    visible = []
    is_displayed_fails = 0
    for e in elems:
        try:
            if e.is_displayed():
                visible.append(e)
        except Exception as e:
            is_displayed_fails += 1
    if is_displayed_fails > 0:
        print("WARN: {} elements failed to eval 'is_displayed'"
              .format(is_displayed_fails))
    return visible


def site_stats(driver=None):
    t = "div"
    l = len(site_body_tag(t))
    print("{}: {}".format(t, l))

    for t in SEMANTIC_TAGS:
        l = len(site_body_tag(t))
        print("{}: {}".format(t, l))


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


def features(elements):
    feats = []
    fails = 0
    for e in elements:
        try:
            f = ElemFeatures(e)
            feats.append(f)
        except Exception as e:
            fails += 1

    if fails > 0:
        print("Failed to get features on {} element(s)".format(fails))
    return feats


class ElemFeatures():
    _element = None  # Selenium element
    _children = []  # Selenium element

    _useful_tag = False  # If the element helps the classifier
    _scanned = False  # If the element was examined
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
        if not self._scanned:
            self.getFeatures()
            self.getTagName()
            self.getText()

        self._scanned = True
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
        self.Tag = self._element.tag_name.lower()
        if self.Tag in SEMANTIC_TAGS:
            self._useful_tag = True
        elif self.Tag == 'div':
            self._useful_tag = True
        pass

    def getText(self):
        self.textSize = len(self._element.text)
        self.textWords = len(self._element.text.split())
        pass
