# -*- coding: utf-8 -*-

import json
import time
import re
import scrapy
import sys
from collections import OrderedDict



class StolplitSpider(scrapy.Spider):
    name = 'stolplit'
    main_url = 'https://www.stolplit.ru'

    def start_requests(self):
        yield scrapy.Request(url=self.main_url, callback=self.parse, method='POST', body="REGION_ID=1&tk=")#, method='POST', body="REGION_ID=1&tk=",

    def parse(self, response):
        for menu in response.xpath('//ul[@class="main-menu-top first_lvl"]/li'):
            self.log(menu.xpath('.//a[@class="menu-type-top__link"]/text()').get())
            yield scrapy.Request(url=self.main_url+menu.xpath('.//a[@class="menu-type-top__link"]/@href').get(), callback=self.iscatalog)
            
    def iscatalog(self, response):
        if response.xpath('//div[@class="whiteBlock"]/ul/li') is not None:
            for item in response.xpath('//div[@class="whiteBlock"]/ul/li'):
                a = item.xpath('.//a/@href')
                yield scrapy.Request(url=self.main_url+a.get(), callback=self.catalog_parse)
        else:
            yield scrapy.Request(url=response.url, callback=self.catalog_parse)

        
    def catalog_parse(self, response):
        next_page =  response.xpath('//a[@class="nextInactive"]/@href').extract_first()
        if next_page is not None:    
            self.log(next_page)
            yield scrapy.Request(url=self.main_url+next_page, callback=self.catalog_parse)

        tovars = response.xpath('//div[@class="info_name"]/a/@href').getall()
        for t in tovars:
            yield scrapy.Request(url= self.main_url + t, callback=self.tovar)

    def tovar(self, response):
        result = OrderedDict()
        result["name"] = response.xpath('//h1[@id="card5name"]/text()').get().replace('                ', '')
        result["catalog"] = response.xpath('//div[@class="linestyle"]/a/span[@itemprop="title"]/text()').getall()[-1]
        result["cost"] = int(response.xpath('//div[@class="card5priceNew"]/meta[@itemprop="price"]/@content').get().replace(' ', ''))
        result["description"] = ""
        #properties
        result_prop = OrderedDict()
        for item in response.xpath('//div[@class="specifications"]/ul[@class="card5infoList"]/li[@class="card5infoRow"]'):
            result_prop[item.xpath('.//span[@class="nowrap"]/text()').get()] = item.xpath('.//span/span[@class="falseTd"]/text()').get()
        color = []
        for item in response.xpath('//span[@itemprop="color"]/text()'):
            color.append(item.get())
        color_string = ""
        for c in color:
            color_string += c + ', '
        color_string = color_string[:-1] 
        color_string = color_string[:-1]     
        result_prop[u'Цвет'] = color_string
        result['mainImage'] = '/assets/images/' + str(response.xpath('//span[@itemtype="https://schema.org/ImageObject"]/img/@data-zoom-image').get()).split("/")[-1]
        result['properties'] = result_prop
        result_image = OrderedDict()
        for item in response.xpath('//span[@class="card5carouselItem slick-slide"]'):
            result_image[str(int(item.xpath('.//a[@class="slider-item"]/@data-img-number').get())-1)] = '/assets/images/' + str(item.xpath('.//a[@class="slider-item"]/@data-orig-image').get()).split("/")[-1]
        

        result['image'] = result_image
        if result['mainImage'] == None:
            result['mainImage'] = '/assets/images/' + str(response.xpath('//span[@itemtype="https://schema.org/ImageObject"]/img/@src').get()).split("/")[-1]
        yield result
        

    def print_data(self, name, catalog, description, cost):
        yield json.loads('{' + '"name": ' + '"' + name + '", "catalog": "' + catalog + '", "description": ' + description + ', "cost": ' + str(int(cost.replace(' ', ''))) + '}')


