# -*- coding: utf-8 -*-

import json
import time
import re
import scrapy
import sys
from collections import OrderedDict



class TriyaSpider(scrapy.Spider):
    name = 'triya'
    main_url = 'https://www.triya.ru'
    actualization_date = str(int(time.time()))
    catalog=[]
    def start_requests(self):
        yield scrapy.Request(url=self.main_url, callback=self.parse)

    def parse(self, response):
        html = response.text
        urls = re.findall(r'<li><a href="(.*)" class.*>', html)

        for url in urls:
            yield scrapy.Request(url=self.main_url+url, callback=self.catalog_parse)
    
    def catalog_parse(self, response):
        tovars = response.xpath('//li[@itemprop="itemListElement"]/a/@href').getall()
        for t in tovars:
            yield scrapy.Request(url= self.main_url + t, callback=self.tovar)


    def tovar(self, response):
        result = OrderedDict()
        result["name"] = response.xpath('//h1[@itemprop="name"]/text()').get()
        result["catalog"] = response.xpath('//a[@itemprop="item"]/@title').getall()[2]
        result["cost"] = int(response.xpath('//div[@id="price"]/text()').get().replace(' ', ''))
        desc = response.xpath('//div[@itemprop="description"]/p/text()').getall()
        text = ""
        for i in range(len(desc)-1):
            text += desc[i] + "\n"
        result["description"] = text
        #properties
        array = []
        for item in response.xpath('//div[@class="prop-group"]'):
            for prop in item.xpath('.//li[@class="prop"]'):
                d = {"key": prop.xpath('.//span[@class="rs"]/span/text()').get(), "value": prop.xpath('.//span[@class="rg"]/text()').get()}
                array.append(d)
        result_prop = OrderedDict()
        result_prop['fieldValue'] = array
        result_prop['fieldSettings'] = {'autoincrement': 1}
        result['properties'] = result_prop
        result['image'] = response.xpath('//div[@class="fotorama"]/img/@src').get() #re.sub(r'(.*\/)', 'image/', response.xpath('//img[@itemprop="image"]/@src').get())
        yield result
        

    def print_data(self, name, catalog, description, cost):
        yield json.loads('{' + '"name": ' + '"' + name + '", "catalog": "' + catalog + '", "description": ' + description + ', "cost": ' + str(int(cost.replace(' ', ''))) + '}')






class TricolorSpider(scrapy.Spider):
    name = 'triya_spider'
    start_urls = [
        'https://www.triya.ru'
    ]
    actualization_date = str(int(time.time()))
    gen_url = "https://www.triya.ru"

    def parse(self, response):
        html = response.body_as_unicode()
        yield json.loads('{"name": "xyq"}')
        
