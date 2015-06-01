#!/usr/bin/python3

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


def getElems(url):
    driver.get(url)
    return driver.find_elements_by_xpath("//*")


def getBodyElems(url):
    driver.get(url)
    return driver.find_elements_by_xpath("/html/body//*")


def getVisibleElems(url):
    elems = getBodyElems(url)
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


from enum import Enum
HTML_Tag = Enum(
    't_a',
    't_abbr',
    't_acronym',
    't_address',
    't_applet',
    't_area',
    't_article',
    't_aside',
    't_audio',
    't_b',
    't_base',
    't_basefont',
    't_bdi',
    't_bdo',
    't_big',
    't_blockquote',
    't_body',
    't_br',
    't_button',
    't_canvas',
    't_caption',
    't_center',
    't_cite',
    't_code',
    't_col',
    't_colgroup',
    't_datalist',
    't_dd',
    't_del',
    't_details',
    't_dfn',
    't_dialog',
    't_dir',
    't_div',
    't_dl',
    't_dt',
    't_em',
    't_embed',
    't_fieldset',
    't_figcaption',
    't_figure',
    't_font',
    't_footer',
    't_form',
    't_frame',
    't_frameset',
    't_h1',
    't_h2',
    't_h3',
    't_h4',
    't_h5',
    't_h6',
    't_head',
    't_header',
    't_hr',
    't_html',
    't_i',
    't_iframe',
    't_img',
    't_input',
    't_ins',
    't_kbd',
    't_keygen',
    't_label',
    't_legend',
    't_li',
    't_link',
    't_main',
    't_map',
    't_mark',
    't_menu',
    't_menuitem',
    't_meta',
    't_meter',
    't_nav',
    't_noframes',
    't_noscript',
    't_object',
    't_ol',
    't_optgroup',
    't_option',
    't_output',
    't_p',
    't_param',
    't_pre',
    't_progress',
    't_q',
    't_rp',
    't_rt',
    't_ruby',
    't_s',
    't_samp',
    't_script',
    't_section',
    't_select',
    't_small',
    't_source',
    't_span',
    't_strike',
    't_strong',
    't_style',
    't_sub',
    't_summary',
    't_sup',
    't_table',
    't_tbody',
    't_td',
    't_textarea',
    't_tfoot',
    't_th',
    't_thead',
    't_time',
    't_title',
    't_tr',
    't_track',
    't_tt',
    't_u',
    't_ul',
    't_var',
    't_video',
    't_wbr')


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
        self.e = elem
        self.getFeatures()
        self.getTagName()
        self.getText()

    def getFeatures(self, e):
        s = self.e.size
        self.s_x = s['width']
        self.s_y = s['height']
        self.s_a = self.sx * self.sy

        l = self.e.location
        self.l_x = l['x']
        self.l_y = l['y']

        l = self.e.location_once_scrolled_into_view
        self.losiv_x = l['x']
        self.losiv_y = l['y']

        pass

    def getTagName(self):
        self.tag = self.e.tag_name
        pass

    def getText(self):
        self.textSize = len(self.e.text)
        self.textWords = len(self.e.text.split)


def main():
    elems = getVisibleElems("http://www.github.com/")

    [ElemFeatures(e) for e in elems]
    pass


if __name__ == '__main__':
    main()
