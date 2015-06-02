import collections
import urlparse

import scrapy
from scrapy.conf import settings
from fake_useragent import UserAgent


DOWNLOADER_MIDDLEWARES = {
  'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
  'scrapper.RandomUserAgentMiddleware': 400
}

settings.set('DOWNLOADER_MIDDLEWARES', DOWNLOADER_MIDDLEWARES)


URLS = []

for line in open('dataset/top-1m.csv'):
  parts = line.split(',')
  url = ''.join(parts[1:]).strip()
  if not url.startswith('http'):
    url = 'http://' + url + '/'
  URLS.append(url)


class RandomUserAgentMiddleware(object):
  def __init__(self):
    super(RandomUserAgentMiddleware, self).__init__()

    self.ua = UserAgent()

  def process_request(self, request, spider):
    request.headers.setdefault('User-Agent', self.ua.random)


class Website(scrapy.Item):
  url = scrapy.Field()
  doctype = scrapy.Field()
  element_hist = scrapy.Field()


class SiteSpider(scrapy.Spider):
  start_urls = URLS
  name = 'sitespider'

  def parse(self, response):
    doctype = response.selector._root.getroottree().docinfo.doctype
    element_hist = collections.defaultdict(int)
    for element in response.xpath('//*'):
      element_hist[element.xpath('name()')[0].extract()] += 1

    yield Website(url=response.url, doctype=doctype,
                  element_hist=dict(element_hist))
