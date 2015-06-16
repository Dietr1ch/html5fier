#!/usr/bin/python3

import collections
import re
import ujson
from urllib.parse import urlparse

import numpy as np

from tags import SEMANTIC_TAGS

import contextlib
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of

SEMANTIC_TAG_SET = set(SEMANTIC_TAGS)
siteRegex = re.compile(r'https?://')

MIN_SIZE = 16

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

    print("# Navigating to '{}'...".format(url))
    driver.get(url)
    wait_for_page_load(driver)
    print("# Done")

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
        print("# WARN: {} elements failed to eval 'is_displayed'"
              .format(is_displayed_fails))
    return visible


def site_stats(driver=None):
    t = "div"
    l = len(site_body_tag(t))
    #print("# div: {}".format(l))

    s = 0
    for t in SEMANTIC_TAGS:
        l = len(site_body_tag(t))
        s += l
        #print("# {}: {}".format(t, l))

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
        print("# Failed to get features on {} element(s)".format(fails))
    return feats

################################################################################
# Element feature base classes.
################################################################################

class ElementFeature:
    """Abstract base class for element features."""

    @property
    def element(self):
        return self.node.element

    def __init__(self, node):
        # FeatureTree node.
        self.node = node
        self.value = None

    def _compute(self):
        raise RuntimeError('Feature not implemented.')

    def compute(self):
        self.value = self._compute()


class AggregateElementFeature(ElementFeature):
    """An element feature that is computed with respect to the aggregate value
    of some other feature across all other elements."""

    # Cache for the aggregate values over node subsets.
    cache = {}

    @classmethod
    def clear_cache(cls):
        cls.cache.clear()

    def __init__(self, node, feature_name=None, aggregate_func=np.mean):
        super(AggregateElementFeature, self).__init__(node)
        self.feature_name = feature_name
        self.aggregate_func = aggregate_func

    def _compute(self):
        agg_value = self.cache_read()
        if agg_value is None:
            values = []
            for node in self.node.tree.root.bfs():
                val = node.get_feature(self.feature_name)
                if val is not None:
                    values.append(val)
            agg_value = self.aggregate_func(values)
            self.cache_write(agg_value)

        return 1. * self.node.get_feature(self.feature_name) / agg_value

    def get_cache_key(self):
        return self.feature_name, self.aggregate_func

    def cache_write(self, value):
        """Saves a value computed over a set of nodes for this specific feature
        to avoid re-computation.
        """
        self.cache[self.get_cache_key()] = value

    def cache_read(self):
        return self.cache.get(self.get_cache_key())


class DescendantElementFeature(ElementFeature):
    """A numerical element feature that is computed with respect to children
    elements with a decay over the descendant degree."""

    def __init__(self, node, feature_name=None, decay=np.exp, agg_func=np.mean,
                 max_depth=None):
        super(DescendantElementFeature, self).__init__(node)
        self.feature_name = feature_name
        self.decay = decay
        self.max_depth = max_depth
        self.agg_func = agg_func

    def _compute(self):
        features_per_level = self.node.get_descendant_feature(self.feature_name,
                                                              self.max_depth)

        level_means = np.zeros((len(features_per_level), 2))

        for i, (level, feature_list) in enumerate(features_per_level.items()):
            level_means[i, 0] = level
            level_means[i, 1] = self.agg_func(np.ravel(feature_list))

        decay = self.decay
        if hasattr(self.decay, '__call__'):
            decay = np.ravel(self.decay(level_means[:, 0]) + .00001)

        weights = 1. / decay
        return np.sum(weights * level_means[:, 1].ravel())


class SiblingElementFeature(ElementFeature):
    """A numerical element feature that is computed with respect to sibling
    (cousin) elements with a decay over the sibling (cousin) degree."""

    def __init__(self, node, feature_name=None, decay=np.exp, agg_func=np.mean,
                 cousin_degree=None):
        super(SiblingElementFeature, self).__init__(node)
        self.feature_name = feature_name
        self.decay = decay
        self.cousin_degree = cousin_degree
        self.agg_func = agg_func

    def _compute(self):
        features_per_level = collections.defaultdict(list)

        features_per_level[0] = [self.node.get_feature(self.feature_name)]

        ancestor_level = 0
        ancestor = self.node
        while True:
            ancestor = ancestor.parent
            ancestor_level += 1
            if ancestor is None:
                break

            if (self.cousin_degree is not None and
                ancestor_level > self.cousin_degree):
                break

            # BFS until we are at the same level.
            for level, relative in ancestor.bfs():
                if level < ancestor_level:
                    continue
                if level > ancestor_level:
                    break
                if relative == self.node:
                    continue

                val = relative.get_feature(self.feature_name)
                if val is not None:
                    features_per_level[level].append(val)

        level_means = np.zeros((len(features_per_level), 2))

        for i, (level, feature_list) in enumerate(features_per_level.items()):
            level_means[i, 0] = level
            level_means[i, 1] = self.agg_func(np.ravel(feature_list))

        decay = self.decay
        if hasattr(self.decay, '__call__'):
            decay = np.ravel(self.decay(level_means[:, 0]) + .00001)

        weights = 1. / decay
        return np.sum(weights * level_means[:, 1])

################################################################################
# Concrete base element features.
################################################################################

class TagFeature(ElementFeature):
    name = 'tag'

    def _compute(self):
        return self.element.tag_name.lower()


class SemanticTagFeature(ElementFeature):
    name = 'semantic_tag'

    def _compute(self):
        return self.element.tag_name.lower() in SEMANTIC_TAG_SET


class WidthFeature(ElementFeature):
    name = 'width'

    def _compute(self):
        return self.element.size['width']


class HeightFeature(ElementFeature):
    name = 'height'

    def _compute(self):
        return self.element.size['height']


class AreaFeature(ElementFeature):
    name = 'area'

    def _compute(self):
        return self.element.size['width'] * self.element.size['height']


class AspectRatioFeature(ElementFeature):
    name = 'aspect_ratio'

    def _compute(self):
        if self.element.size['height'] == 0:
            return -1

        return 1. * self.element.size['width'] / self.element.size['height']


class XFeature(ElementFeature):
    name = 'x'

    def _compute(self):
        return self.element.location['x']


class YFeature(ElementFeature):
    name = 'y'

    def _compute(self):
        return self.element.location['y']


class VisibleXFeature(ElementFeature):
    name = 'visible_x'

    def _compute(self):
        return self.element.location_once_scrolled_into_view['x']


class VisibleYFeature(ElementFeature):
    name = 'visible_y'

    def _compute(self):
        return self.element.location_once_scrolled_into_view['y']


class TextCharLengthFeature(ElementFeature):
    name = 'text_length'

    def _compute(self):
        return len(self.element.text)


class TextWordLengthFeature(ElementFeature):
    name = 'text_words'

    def _compute(self):
        return len(self.element.text.split())


class ChildrenCountFeature(ElementFeature):
    name = 'children_count'

    def _compute(self):
        return len(self.node.children)


class LinkCountFeature(ElementFeature):
    name = 'link_count'

    def _compute(self):
        anchors = self.node.element.find_elements_by_xpath('./a')

        return len(anchors)


class InternalLinkCountFeature(ElementFeature):
    name = 'internal_link_count'

    def _compute(self):
        site = urlparse(self.node.tree.site).netloc

        count = 0
        hrefs = self.node.element.find_elements_by_xpath('./a')

        for h in hrefs:
            url = urlparse(h.get_attribute('href'))
            if not url.netloc or site in url.netloc:
                count += 1

        return count


BASE_FEATURES = (
    #TagFeature,
    SemanticTagFeature,
    WidthFeature,
    HeightFeature,
    AreaFeature,
    AspectRatioFeature,
    XFeature,
    YFeature,
    VisibleXFeature,
    VisibleYFeature,
    TextCharLengthFeature,
    TextWordLengthFeature,
    ChildrenCountFeature,
    LinkCountFeature,
    InternalLinkCountFeature,
)

DESCENDANT_ELEMENT_FEATURES = [
    ('descendant_count', dict(feature_name='children_count',
                              decay=1.,
                              agg_func=np.sum)),
    ('descendant_score', dict(feature_name='children_count',
                              agg_func=np.sum)),
    ('descendant_link_count', dict(feature_name='link_count',
                                   decay=1., agg_func=np.sum)),
    ('descendant_link_score', dict(feature_name='link_count',
                                   agg_func=np.sum)),
    ('descendant_internal_link_count',
     dict(feature_name='internal_link_count',
          decay=1., agg_func=np.sum)),
    ('descendant_internal_link_count',
     dict(feature_name='internal_link_count', agg_func=np.sum)),
]

SIBLING_ELEMENT_FEATURES = [
    ('sibling_link_count', dict(feature_name='link_count',
                                decay=1., agg_func=np.sum)),
    ('sibling_link_score', dict(feature_name='link_count',
                                agg_func=np.sum)),
    ('sibling_internal_link_count',
     dict(feature_name='internal_link_count',
          decay=1., agg_func=np.sum)),
    ('sibling_internal_link_count',
     dict(feature_name='internal_link_count', agg_func=np.sum)),
]

AGGREGATE_ELEMENT_FEATURES = []


class FeatureTree:

    class Node:
        def __init__(self, element, tree, parent=None):
            self.tree = tree
            self.element = element
            self.parent = parent
            self.children = set()
            self.features = {}

            self.use = element.size['width'] > MIN_SIZE and element.size['height'] > MIN_SIZE

        def bfs(self):
            open_list = [(0, self)]

            while open_list:
                depth, node = open_list.pop(0)
                yield depth, node

                for child in node.children:
                    open_list.append((depth + 1, child))

        def get_feature(self, feature_name):
            if feature_name in self.features:
                return self.features[feature_name].value
            return None

        def get_descendant_feature(self, feature_name, max_depth=None):
            """Returns a dict with features for descendants by level."""
            features = collections.defaultdict(list)

            for depth, node in self.bfs():
                if max_depth is not None and depth > max_depth:
                    break
                val = node.get_feature(feature_name)
                if val is not None:
                    features[depth].append(val)

            return features

    def __iter__(self):
        for _, node in self.root.bfs():
            yield node

    def __init__(self, driver=None):
        self.driver = get_driver(driver)

        self.site = self.driver.current_url

        root = self.driver.find_element_by_xpath("/html/body")
        self.root = self.build_tree(root, tree=self)

        # Compute features in order of dependence.
        self.compute_features(self.root, BASE_FEATURES)

        self.compute_relative_features(self.root, DescendantElementFeature,
                                       DESCENDANT_ELEMENT_FEATURES)
        self.compute_relative_features(self.root, SiblingElementFeature,
                                       SIBLING_ELEMENT_FEATURES)
        self.compute_relative_features(self.root, AggregateElementFeature,
                                       AGGREGATE_ELEMENT_FEATURES)

    @classmethod
    def build_tree(cls, element, parent=None, tree=None):
        # if depthLimit == 0:
        # return

        node = cls.Node(element, tree, parent)

        # Add children.
        for child_element in children(element):
            node.children.add(cls.build_tree(child_element, node, tree))

        return node

    @classmethod
    def compute_features(cls, root_node, feature_set):
        if root_node.use:
            try:
                for feature_class in feature_set:
                    feature = feature_class(root_node)
                    feature.compute()
                    root_node.features[feature_class.name] = feature
            except Exception as e:
                print('# Failed to extract feature {}: {}'.format(
                    feature_class.name, e.__class__.__name__))
                root_node.use = False

        for child_node in root_node.children:
            cls.compute_features(child_node, feature_set)

    @classmethod
    def compute_relative_features(cls, root_node, feature_class, feature_set):
        if root_node.use:
            try:
                for feature_name, feature_kwargs in feature_set:
                    feature = feature_class(root_node, **feature_kwargs)
                    setattr(feature, 'name', feature_name)
                    feature.compute()
                    root_node.features[feature_name] = feature
            except Exception as e:
                print('# Failed to extract feature {}: {}'.format(
                    feature_name, e.__class__.__name__))
                root_node.use = False

        for child_node in root_node.children:
            cls.compute_relative_features(child_node, feature_class,
                                          feature_set)

