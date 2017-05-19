# -*- coding:utf-8 -*-
from scrapy import cmdline

cmdline.execute("scrapy crawl NewsSpider -o news.json".split())