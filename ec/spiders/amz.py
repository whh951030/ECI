# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_redis.spiders import RedisCrawlSpider
import re
import redis


conn = redis.Redis(host='127.0.0.1',port=6379)
conn.lpush('amz', 'https://www.amazon.cn/s/ref=nb_sb_noss?__mk_zh_CN=%E4%BA%9A%E9%A9%AC%E9%80%8A%E7%BD%91%E7%AB%99&url=search-alias%3Dstripbooks&field-keywords=')


class AmzSpider(RedisCrawlSpider):
    name = 'amz'
    allowed_domains = ['amazon.cn']
    redis_key = 'amz'
    rules = (
        Rule(LinkExtractor(restrict_xpaths='//*[@id="leftNav"]/ul[1]/ul/div/li'), follow=True),
        Rule(LinkExtractor(restrict_xpaths='//*[@id="pagn"]'), follow=True),
        Rule(LinkExtractor(restrict_xpaths='//a[contains(@class, "s-access-detail-page")]'), callback='parse_item'),
    )

    def parse_item(self, response):
        item = {}
        item['book_name'] = response.xpath('//*[contains(@id,"roductTitle")]/text()').extract_first()
        item['book_img'] = response.xpath('//*[contains(@id, "mgBlkFront")]/@src').extract_first()
        item['book_url'] = response.url
        item['book_author'] = ''.join(response.xpath('//*[@id="bylineInfo"]/span/a/text()').extract())
        item['book_price'] = response.xpath('//span[contains(@class, "a-color-price")]/text()').extract_first()

        publish = re.findall('<li><b>出版社:</b> (.+?);.*?\((.+?)\)</li>', response.text)
        if len(publish) != 0:
            item['book_publisher'] = publish[0][0]
            item['book_publish_date'] = publish[0][1]

        a_s = response.xpath('//span[@class="a-list-item"]/a[text()]')
        if len(a_s) > 0:
            item['b_category_name'] = a_s[0].xpath('./text()').extract_first().strip()
            item['b_category_url'] = response.urljoin(a_s[0].xpath('./@href').extract_first())
        if len(a_s) > 1:
            item['m_category_name'] = a_s[1].xpath('./text()').extract_first().strip()
            item['m_category_url'] = response.urljoin(a_s[1].xpath('./@href').extract_first())
        if len(a_s) > 2:
            item['s_category_name'] = a_s[2].xpath('./text()').extract_first().strip()
            item['s_category_url'] = response.urljoin(a_s[2].xpath('./@href').extract_first())
        yield item
