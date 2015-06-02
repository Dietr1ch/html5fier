#!/usr/bin/python3

import sys
import re
import ujson
from selenium import webdriver
# from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.support.ui import WebDriverWait # 2.4.0
# from selenium.webdriver.support import expected_conditions as EC # 2.26.0

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
    e = None  # Selenium element
    s_x = -1  # Width
    s_y = -1  # Height
    s_a = -1  # Area

    l_x = -1  # X
    l_y = -1  # Y

    losiv_x = -1  # X
    losiv_y = -1  # Y

    tag = ""

    textSize = -1
    textWords = -1

    def __init__(self, elem):
        self.getFeatures(elem)
        self.getTagName(elem)
        self.getText(elem)

    def getFeatures(self, elem):
        s = elem.size
        self.s_x = s['width']
        self.s_y = s['height']
        self.s_a = self.s_x * self.s_y

        l = elem.location
        self.l_x = l['x']
        self.l_y = l['y']

        l = elem.location_once_scrolled_into_view
        self.losiv_x = l['x']
        self.losiv_y = l['y']

        pass

    def getTagName(self, elem):
        self.tag = elem.tag_name
        pass

    def getText(self, elem):
        self.textSize = len(elem.text)
        self.textWords = len(elem.text.split())


def main():
    for site in sys.stdin:
        site = site.strip()
        elems = getVisibleElems(site)
        features = [ElemFeatures(e) for e in elems]

        j = ujson.dumps(
            {
                'site': site,
                'features': features,
            })

        print("{}, {}\n".format(site, j))


if __name__ == '__main__':
    main()
