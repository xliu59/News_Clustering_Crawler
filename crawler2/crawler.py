# -*- coding: utf-8 -*-
# filename: crawler.py

import sqlite3  
from urllib import request, parse, error
import re
import json
import time
from datetime import date, timedelta, datetime
from html.parser import HTMLParser 



class HREFParser(HTMLParser):  
    """
    Parser that extracts hrefs, titles, pics
    """
    hrefs = set()
    title = None
    image = None
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            dict_attrs = dict(attrs)
            if dict_attrs.get('href'):
                self.hrefs.add(dict_attrs['href'])
        if tag in ('title', 'h1') and self.title == None:
            self.title = 'waiting'
        if tag == 'img' and self.image == None:
            dict_attrs = dict(attrs)
            if dict_attrs.get('src') \
                and re.match("^http[s]?://.*(png|jpg|gif)$", dict_attrs.get('src')) \
                and not re.match(".*logo.*", dict_attrs.get('src')) \
                and not re.match("^http[s]?://static.*(bbc|cnn)[a-zA-Z0-9-]+.(jpg|png|gif)$", dict_attrs.get('src')):
#                print "here!", dict_attrs.get('src')
                self.image = dict_attrs.get('src')

    def handle_data(self, data):
        if self.title == 'waiting':
#            print ("Title =", data)
            self.title = data

class DateParser(HTMLParser):  
    """
    Parser that extracts article date
    """
    article_date = None
    def handle_starttag(self, tag, attrs):
        if tag == 'div' and dict(attrs).get('class') and self.article_date == None:
            dict_attrs = dict(attrs)
#            print "!!!!", type(dict_attrs.get('class'))
            if re.match("^date date--v2.*$", dict_attrs.get('class')):
#                print "date found by parser:", dict_attrs.get('data-datetime')
                self.article_date = dict_attrs.get('data-datetime')
        return self.article_date

def get_local_infos(html, domain):  
    """
    Read through HTML content and returns a tuple of links
    internal to the given domain
    """
    hrefs = set()
    parser = HREFParser()
    parser.feed(html)
    for href in parser.hrefs:
        u_parse = parse.urlparse(href)
        if href.startswith('/'):
            # purposefully using path, no query, no hash
            hrefs.add(u_parse.path)
        else:
          # only keep the local urls
          if u_parse.netloc == domain:
            hrefs.add(u_parse.path)
#    print "is hrefs correct?", parser.hrefs
#    print ("hrefs on this page:", hrefs)
    print ("Articile Title:", parser.title)
    print ("Article Image:", parser.image)
    return {"hrefs" : hrefs, "title": parser.title, "image": parser.image}


class CrawlerCache(object):  
    """
    Crawler data caching per relative URL and domain.
    """
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS sites
            (domain text, url text, content text, title text, image, PRIMARY KEY (domain, url))''')
        self.conn.commit()
        self.cursor = self.conn.cursor()

    def set(self, domain, url, html, title, image):
        """
        store the content for a given domain and relative url
        """
        try:
            #if domain == 'money.cnn.com':
            #    temp = 'http://' + domain + url
            #else:
            temp = 'http://' + domain + url
            self.cursor.execute("INSERT OR REPLACE INTO sites VALUES (?,?,?,?,?)",
            (domain, temp, html, title, image))
            self.conn.commit()
        except Exception as e:
#            print "fail to insert data to db, may already exist!"
            print (e)


    def get(self, domain, url):
        """
        return the content for a given domain and relative url
        """
        self.cursor.execute("SELECT content FROM sites WHERE domain=? and url=?",
            (domain, url))
        row = self.cursor.fetchone()
        if row:
            return row[0]

    def get_urls(self, domain):
        """
        return all the URLS within a domain
        """
        self.cursor.execute("SELECT url FROM sites WHERE domain=?", (domain,))
        # could use fetchone and yield but I want to release
        # my cursor after the call. I could have create a new cursor tho.
        # ...Oh well
        return [row[0] for row in self.cursor.fetchall()]

    def get_output(self, domain):
        """
        return title, image, url under the speficied domain
        """
        self.cursor.execute("SELECT title, image, url FROM sites")
        return [row[0:3] for row in self.cursor.fetchall()]


class Crawler(object):  
    def __init__(self, cache=None, depth=100):
        """
        depth: how many time it will bounce from page one (optional)
        cache: a basic cache controller (optional)
        """
        self.depth = depth
        self.content = {}
        self.cache = cache
        self.count = 0
        self.check_date_list = ['www.bbc.com',]

    def crawl(self, url, no_cache=None, only_cache=None):
        """
        url: where we start crawling, should be a complete URL like
        'http://www.intel.com/news/'
        no_cache: function returning True if the url should be refreshed
        """
        u_parse = parse.urlparse(url)
        self.domain = u_parse.netloc
        self.content[self.domain] = {}
        self.scheme = u_parse.scheme
        self.no_cache = no_cache
        self.only_cache = only_cache
        self._crawl([u_parse.path], self.depth)
        self.dump_file(self.domain)

    def set(self, url, html, title, image):
        if url not in self.content[self.domain]:
            self.content[self.domain][url] = {}
        self.content[self.domain][url] = {"html": html, "title": title, "image": image}
        if self.is_cacheable(url):
            self.cache.set(self.domain, url, html, title, image)

    def get(self, url):
        page = None
        if self.is_cacheable(url):
          page = self.cache.get(self.domain, url)
        if page is None:
          page = self.curl(url)
        else:
            print ("\n", self.count, ".cached url... [%s] %s" % (self.domain, url))
        return page

    def is_cacheable(self, url):
        return self.cache \
            and self.no_cache \
            and not self.no_cache(url)

    def _crawl(self, urls, max_depth):
        n_urls = set()
        if max_depth:
#            print "max_depth=", max_depth
            for url in urls:
#                print self.count, ".new url = ", url
                if max_depth < self.depth and self.only_cache and not self.only_cache(url):
                    #print "not what i want!! - ", url
                    continue
                # do not crawl twice the same page
                if url in self.content or url  in self.content[self.domain]:
                    continue
                self.count += 1
                html = self.get(url)
                flag = True
                if self.domain in (self.check_date_list):
                    flag = self.check_date(html, max_depth, url)                   
                if flag == True:
                    res_map = get_local_infos(html, self.domain)
                    #pic = self.get_pic(html)
                    if max_depth != self.depth:
                        self.set(url, html, res_map["title"], res_map["image"])
                    n_urls = n_urls.union(res_map["hrefs"])
                else:
                    print ("*** page outdated, will not crawl")
                #print ("urls=", n_urls)
            self._crawl(n_urls, max_depth-1)

    def curl(self, url):
        """
        return content at url.
        return empty string if response raise an HTTPError (not found, 500...)
        """
        try:
            print ("\n", self.count,".retrieving url... [%s] %s" % (self.domain, url))
            req = request.Request('%s://%s%s' % (self.scheme, self.domain, url))
            response = request.urlopen(req)
            return response.read().decode('ascii', 'ignore')
        except error.HTTPError as e:
            print ("error [%s] %s: %s" % (self.domain, url, e))
            return ''

    def dump_file(self, domain):
        res_list = []
        """
        save data to a single file
        file content is json format
        file is named by domain
        """
        info_list = self.cache.get_output(domain)
#        print info_list
        for info in info_list:
#            print ("domain=", domain)
            info_map = {}
            info_map["headline"] = info[0]
            info_map["image"] = info[1]
            info_map["link"] = info[2]
            res_list.append(info_map)
#            print ("res_list=", res_list)
#            print info_map
        print (json.dumps(res_list))
        with open('res.json', 'w+') as outfile:
            outfile.write(json.dumps(res_list))

    def check_date(self, html, depth, url):
        parser = DateParser()
        parser.feed(html)
        if depth == self.depth:
            return True
        elif parser.article_date == None:
            return False
        else:
#            print ("need to check date, url=", url, "depth=", depth)
            print ("current time:", time.strftime("%d %B %Y"))
            article_date = datetime.strptime(parser.article_date, '%d %B %Y')
            if article_date >= (datetime.now() - timedelta(days = 7)) \
                and article_date <= datetime.today():
                print ("Article Time:", parser.article_date)
                return True