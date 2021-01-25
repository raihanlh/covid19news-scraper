# -*- usage : scrapy runspider detik_covid19.py -s JOB_DIR=. -o covid.json
import scrapy
import datetime
import lxml
from scrapy.http import FormRequest
from scrapy import Request
import logging
from inspect import getmembers
from pprint import pprint
from bs4 import BeautifulSoup, Tag
import re

class DetikSpider(scrapy.Spider):
    name = "detik"
    allowed_domains = ["news.detik.com"]
    logging.log(logging.INFO, "test--")
    max_pages = 10

    def start_requests(self):
        form_requests = []
        start_urls = []
        max_pg = self.max_pages+1
        for i in range(1,max_pg):
            logging.log(logging.INFO, "page=")
            logging.log(logging.INFO, str(i))

            req = Request("https://www.detik.com/tag/corona/?sortby=time&page="+str(i), callback = self.parse)
            req.meta['url'] = "https://www.detik.com/tag/corona/?sortby=time&page="+str(i)
            form_requests.append(req)
        return form_requests

    def parse(self, response):
      for href in response.css(".list-berita a::attr(href)"):
          full_url = response.urljoin(href.extract())
          req = scrapy.Request(full_url, callback=self.parse_news)
          yield req

    def parse_news(self,response):
        yield {
            'title': remove_markup_title(response.css('h1.detail__title').extract()[0]).strip(),
            'text': remove_markup(response.css("div.detail__body-text").extract()[0]),
            'url': response.url,
            'date': " ".join(remove_markup(response.css("div.detail__date").extract()[0]).split(" ")[1:-1])
        }

def remove_cdata(txt):
    beg = txt.find('<!--')
    txt = txt[:beg]
    return txt

def remove_markup(txt):
    soup = BeautifulSoup(txt, "html.parser")
    txt = soup.get_text()
    txt = txt.replace("\t","").replace("\n","").replace("\\\\\\","").replace("\\","").replace('\"','"')
    txt = remove_cdata(txt)
    txt = re.sub('\ {2,}', '', txt)
    logging.log(logging.INFO, "txt=")
    logging.log(logging.INFO, txt)
    return txt

def remove_markup_title(txt):
    soup = BeautifulSoup(txt, "html.parser")
    txt = soup.get_text()
    txt = txt.replace("\t","").replace("\n","").replace("\\\\\\","").replace("\\","").replace('\"','"')
    print(txt)
    return txt

def remove_html_markup(arr):
    result = []
    for s in arr:
        s2 = lxml.html.fromstring(s).text_content()
        s3 = s2.encode('ascii', 'ignore')
        s3 = s3.translate(None, '\t\n')
        result.append(s3)
    return result
