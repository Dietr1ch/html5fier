import collections
import urlparse

import scrapy
from scrapy.conf import settings
from fake_useragent import UserAgent


URLS = (
  'http://www.alexa.com/topsites/category;0/Top/News',
  #'http://www.alexa.com/topsites/category/Top/Arts',
  #'http://www.alexa.com/topsites/category/Top/Business',
  #'http://www.alexa.com/topsites/category/Top/Computers',
  #'http://www.alexa.com/topsites/category/Top/Games',
  #'http://www.alexa.com/topsites/category/Top/Health',
  #'http://www.alexa.com/topsites/category/Top/Home',
  #'http://www.alexa.com/topsites/category/Top/Kids_and_Teens',
  #'http://www.alexa.com/topsites/category/Top/Recreation',
  #'http://www.alexa.com/topsites/category/Top/Science',
  #'http://www.alexa.com/topsites/category/Top/Shopping',
  #'http://www.alexa.com/topsites/category/Top/Sports',
  #'http://www.alexa.com/topsites/category/Top/Society',
  #'http://www.alexa.com/topsites/category/Top/Reference',
  #'http://www.alexa.com/topsites/category/Top/Regional',
)


DOWNLOADER_MIDDLEWARES = {
  'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
  'scrapper.RandomUserAgentMiddleware': 400
}

settings.set('DOWNLOADER_MIDDLEWARES', DOWNLOADER_MIDDLEWARES)


class RandomUserAgentMiddleware(object):
  def __init__(self):
    super(RandomUserAgentMiddleware, self).__init__()

    self.ua = UserAgent()

  def process_request(self, request, spider):
    request.headers.setdefault('User-Agent', self.ua.random)


class Website(scrapy.Item):
  url = scrapy.Field()
  element_hist = scrapy.Field()


class BlogSpider(scrapy.Spider):
  start_urls = URLS
  name = 'sitespider'

  def parse(self, response):
    # Listed websites.
    for listing in response.css('.site-listing .desc-container'):
      url = listing.css('.desc-paragraph a::attr(href)')
      if not url:
        continue

      url = url[0].extract()
      if not url.startswith('/siteinfo/'):
        continue

      url = url[len('/siteinfo/'):]
      if not url.startswith('http'):
        url = 'http://' + url

      yield scrapy.Request(url, callback=self.parse_site)

    # Next page.
    next_url = response.css('.alexa-pagination a.next::attr(href)')
    if next_url:
      next_url = next_url.extract()[0]
      next_url = urlparse.urljoin(response.url, next_url)
      yield scrapy.Request(next_url)

  def parse_site(self, response):
    element_hist = collections.defaultdict(int)
    for element in response.xpath('//*'):
      element_hist[element.xpath('name()')[0].extract()] += 1

    yield Website(url=response.url, element_hist=dict(element_hist))
