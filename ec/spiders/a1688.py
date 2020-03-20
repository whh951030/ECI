# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import quote


class A1688Spider(scrapy.Spider):
    name = '1688'
    allowed_domains = ['1688.com']
    with open('input.txt', 'r', encoding='utf-8')as f:
        keywordstr = f.readline()
        f.close()
    keyword = quote(keywordstr, encoding='gbk')
    page = 1
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'referer': 'https://www.1688.com/'
    }
    start_urls = ['https://1688.com']

    def parse(self, response):
        seach_url = 'https://s.1688.com/selloffer/offer_search.htm?keywords={}&n=y&netType=1%2C11&encode=utf-8&spm=a260k.dacugeneral.search.0'.format(self.keyword)
        yield scrapy.Request(
                    url=seach_url,
                    callback=self.parse_list,
                    headers=self.headers
                    # meta={'item': copy.deepcopy(item)}
                )

    def parse_list(self, response):
        #  https://detail.1688.com/offer/597627781557.html?clickid=db79f70e97ba4557a6590450c3c2b110&sessionid=8432c87670a448c65271639e7e051d61
        li_list_name = response.xpath('//*[@class="sm-offer-item sw-dpl-offer-item "]//a')
        offerid = li_list_name.xpath('//*/a/@offerid').extract()
        for i in set(offerid):
            detail_url = 'https://detail.1688.com/offer/{}.html?clickid=db79f70e97ba4557a6590450c3c2b110&sessionid=8432c87670a448c65271639e7e051d61'.format(i)
            # print(detail_url)
            yield scrapy.Request(
                url=detail_url,
                callback=self.parse_detail,
                headers=self.headers,
                dont_filter=True
                # meta={'item': copy.deepcopy(item)}
            )
        maxpage = response.xpath('//*/div/@data-total-page').extract_first()
        if self.page < int(maxpage):
            self.page += 1
            seach_url = 'https://s.1688.com/selloffer/offer_search.htm?keywords={}&n=y&netType=1%2C11&encode=utf-8&spm=a260k.dacugeneral.search.0&beginPage={}#sm-filtbar'.format(self.keyword, self.page)
            yield scrapy.Request(
                url=seach_url,
                callback=self.parse_list,
                headers=self.headers
                # meta={'item': copy.deepcopy(item)}
            )

    def parse_detail(self, response):
        try:
            with open('name.txt', 'a')as f:
                f.write(response.xpath('//*[@id="mod-detail-title"]/h1/text()').extract_first())
                f.write('\t')
                f.write(response.url)
                f.write('\n'*2)
                f.close()
        except:
            pass
