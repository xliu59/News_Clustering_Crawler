#!/usr/bin/python
# filename: run.py
import re
import time
from crawler import Crawler, CrawlerCache

#if __name__ == "__main__": 
    # Using SQLite as a cache to avoid pulling twice
crawler = Crawler(CrawlerCache('crawler.db'))
root_re = re.compile('^/$').match
year = time.strftime("%Y")
month = time.strftime("%m")
date = time.strftime("%d")
section = "technology"
    
cnn_url_pattern = re.compile('^/%s/%s/17/%s/.*\.html$' % (year, month, section)).match
bbc_url_pattern = re.compile('^/news/technology-[0-9]+$').match 

crawler.crawl('http://money.cnn.com/technology/', no_cache=root_re, only_cache=cnn_url_pattern)
crawler.crawl('http://www.bbc.com/news/technology', no_cache=root_re, only_cache=bbc_url_pattern)

#    crawler.crawl('http://www.engadget.com/', no_cache=root_re)
#    crawler.crawl('http://gizmodo.com/', no_cache=root_re)
#    crawler.crawl('http://www.zdnet.com/', no_cache=root_re)
#    crawler.crawl('http://www.wired.com/', no_cache=root_re)
    