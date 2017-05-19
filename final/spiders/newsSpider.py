# -*- coding:utf-8 -*-
import scrapy

class NewsItem(scrapy.Item):
    headline = scrapy.Field()
    link = scrapy.Field()
    image = scrapy.Field()

class NewsSpider(scrapy.Spider):
    name = 'NewsSpider'

    start_urls = ['https://www.nytimes.com/section/technology']

    def parse(self, response):
        # follow links to author pages
        #yield {
        #    'title': response.xpath('//title/text()').extract_first(),
            #'headline': response.xpath('//li/article/div/h2/a/text()').extract_first(),
        #}

        allItems = []
        for techNews in response.xpath('//li'):
            item = NewsItem()
            item['headline'] = techNews.xpath('./article/div/h2/a/text()').extract_first()
            item['link'] = techNews.xpath('./article/div/h2/a/@href').extract_first()
            item['image'] = techNews.xpath('./article/figure/a/img/@src').extract_first()
                #'datetime': temp[24: 34],
            allItems.append(item)
            yield item
            

        for techNews in response.xpath('//div[@class="stream"]/ol/li'):
            item = NewsItem()
            item['headline'] = techNews.xpath('./article/div/a/div/h2/text()').extract_first().strip()
            item['link'] = techNews.xpath('./article/div/a/@href').extract_first()
            item['image'] = techNews.xpath('./article/div/a/div/img/@src').extract_first()
                #'datetime': techNews.xpath('./article/div/a/@href').extract_first()[24: 34],
            allItems.append(item)
            yield item
                





        # for href in response.css('.headline + a::attr(href)').extract():
        #     yield scrapy.Request(response.urljoin(href),
        #                          callback=self.parse_author)

    # def parse_author(self, response):
    #     def extract_with_css(query):
    #         return response.css(query).extract_first().strip()

    #     yield {
    #     	'Title': extract_with_css('title'),
    #         #'Link': extract_with_css('link.canonical::text'),
    #     }




# class NewsSpider(scrapy.Spider):
#     name = 'news'

#     start_urls = ['http://quotes.toscrape.com']

#     def parse(self, response):
#         # follow links to author pages
#         for href in response.css('.author + a::attr(href)').extract():
#             yield scrapy.Request(response.urljoin(href),
#                                  callback=self.parse_author)

#     def parse_author(self, response):
#         def extract_with_css(query):
#             return response.css(query).extract_first().strip()

#         yield {
#         	'Name': extract_with_css('title'),
#             'DOB': extract_with_css('.author-born-date::text'),
#         }