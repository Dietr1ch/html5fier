#!/usr/bin/python3

import re
import ujson

from tags import SEMANTIC_TAGS

import contextlib
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of

siteRegex = re.compile(r'https?://')

global dri
dri = None


def to_json(elemFeature):
    elemJSON = ujson.dumps(elemFeature)
    print("  {}".format(elemJSON))
    return elemJSON


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
    print("div: {}".format(l))

    s = 0
    for t in SEMANTIC_TAGS:
        l = len(site_body_tag(t))
        s += l
        print("{}: {}".format(t, l))

    return s


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

    def __init__(self, elem):
        self.default_values()

        # Set up
        self._element = elem
        self._children = children(elem)

        # Calculate features
        self.features_tag_name()
        if True or self._useful_tag:
            self.features_render()
            self.features_text()
            self.features_style()
            self.features_tree()
        pass

    def default_values(self):

        # Element data
        # ============

        self._element = None  # Selenium element
        self._children = []  # Selenium elements

        self._useful_tag = False  # If the element helps the classifier
        self.Tag = ""

        # Element features
        # ----------------

        # Element size and location
        self.size_x = -1  # Width
        self.size_y = -1  # Height
        self.size_area = -1  # Area
        self.location_x = -1  # X
        self.location_y = -1  # Y
        self.location_visible_x = -1  # X
        self.location_visible_y = -1  # Y

        # Element text data
        self.text_size = -1
        self.text_words = -1

        # Pending Features
        # ----------------

        # Children data
        #   * children_count = 0
        #   * children_normalized_histogram = []

        # Links inside tree
        #   * links_tree_relative = 0
        #   * links_tree_same_site = 0
        #   * links_tree_external = 0
        # Direct children links
        #   * links_children_relative = 0
        #   * links_children_same_site = 0
        #   * links_children_external = 0

        # Style
        # -----
        #   * font_size_px = -1
        #   * font_bold = None  # None, False, True
        #   * font_italic = None
        #   * font_color = None
        pass

    def features_tag_name(self):
        self.Tag = self._element.tag_name.lower()
        if self.Tag in SEMANTIC_TAGS:
            self._useful_tag = True
        elif self.Tag == 'div':
            self._useful_tag = True
        pass

    def features_render(self):
        s = self._element.size
        self.size_x = s['width']
        self.size_y = s['height']
        self.size_area = self.size_x * self.size_y

        l = self._element.location
        self.location_x = l['x']
        self.location_y = l['y']

        l = self._element.location_once_scrolled_into_view
        self.location_visible_x = l['x']
        self.location_visible_y = l['y']
        pass

    def features_text(self):
        self.text_size = len(self._element.text)
        self.text_words = len(self._element.text.split())
        pass

    def features_style(self):
        pass

    def features_tree(self):
        self.features_tree_links()
        self.features_tree_images()
        pass

    def features_tree_links(self):
        pass

    def features_tree_images(self):
        pass


class FeatureTree:

    def __init__(self, driver=None):
        self._driver = get_driver(driver)

        self.site = self.driver.current_url
        self.elements = site_visible_elements(self.driver)

        root = self._driver.find_element_by_xpath("/html/body")
        self.root = self.build_tree(root)

    @staticmethod
    def build_tree(element, depthLimit=-1):
        # if depthLimit == 0:
        # return
        return {'element': element,
                'features': ElemFeatures(element),
                'children': [FeatureTree.build_tree(c)
                             for c in children(element, depthLimit-1)]
                }
