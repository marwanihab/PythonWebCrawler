import logging
import scrapy
import time
from pydispatch import dispatcher
from scrapy import signals
import re


class WikipediaPhilosophySpider(scrapy.Spider):
    name = 'wikipedia_philosophy'
    allowed_domains = ['en.wikipedia.org']
    start_urls = ['https://en.wikipedia.org/wiki/Special:Random']
    target_url = "/wiki/Philosophy"
    visited_urls = {}
    loop = True
    first_url = '/wiki/Special:Random'

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        if spider is not self:
            return
        if self.loop:
            print("Crawler either terminated or reached a loop !!")

    def parse(self, response):

        print("Link visited https://en.wikipedia.org/", self.first_url)

        if self.first_url == self.target_url:
            print("Target link has been reached")
            self.loop = False
            return

        else:
            self.visited_urls[self.first_url] = self.first_url

        # Extract the first link url
        self.first_url = None

        self.first_url = response.xpath(
            "//div[@class='mw-content-ltr']/div[@class='mw-parser-output']/p[not (@class='mw-empty-elt')]").extract_first()


        self.first_url = self.parse_P(str(self.first_url), response)

        if self.first_url is None:
            print("Article has no links")
            self.loop = False
            return

        time.sleep(0.5)
        # dont_filter = True
        yield scrapy.Request(response.urljoin(self.first_url), self.parse)

    def parse_P(self, paragraph, response):

        if "(" not in paragraph:
 
            return response.xpath(
                "//div[@class='mw-content-ltr']/div[@class='mw-parser-output']/p/a/@href").extract_first()
        else:
            # to remove all the <a> tags between brackets
            # proper_paragraph = re.sub(r'\([^)]*\)', '', str(paragraph))
            proper_paragraph = re.sub(
                r'\([^)]*<a.*?</a>[^)]*\)', '', str(paragraph))
            # to remove all the <a> tags with <small> styling
            proper_paragraph = re.sub(r'small.*?small', '', proper_paragraph)
            # to remove all the <a> tags with <sup> styling
            proper_paragraph = re.sub(r'sup.*?sup', '', proper_paragraph)
            # to remove all the <a> tags with <span> styling
            proper_paragraph = re.sub(r'span.*?span', '', proper_paragraph)

       

            return self.extract_proper_link(proper_paragraph)

    def extract_proper_link(self, paragraph):

        # to get the first link start index
        link_index = paragraph.find('<a href=')
        link_index = link_index + 9  # 9 the length of <a href= and the starting quote '
        link = ""
        for x in range(link_index, len(paragraph)):
            if paragraph[x] != " ":
                link = link + paragraph[x]
            else:
                break  # stop when it reaches the space

        link = link[:-1]  # remove the ending quote
        return link
