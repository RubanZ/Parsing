import scrapy
import json
from scrapy.crawler import CrawlerProcess
import datetime
from time import time
import sys
import re
import scrapy
import sys

class QuotesSpider(scrapy.Spider):
    name = "poehalisnami_spider"
    def start_requests(self):
        url_city = "    "
        yield scrapy.Request(url=url_city,
                             method="POST",
                             headers={"Content-Type": "application/json"},
                             callback=self.parse_map
                             )

    def parse_map(self, response):
        data = json.loads(response.body_as_unicode())
        for city_id in data["CityDropDownList"]["Items"]:
            if not city_id["Value"] == "":
                url_data = "https://www.poehalisnami.ua/api/office/officelistformap"
                res = {"languageId": "2", "cityId": city_id["Value"]}
                yield scrapy.Request(url=url_data,
                                     body=json.dumps(res).encode('utf8'),
                                     method="POST",
                                     headers={'Accept': '','Content-Type': 'application/json'},
                                     callback=self.parse_city
                                     )

    def parse_city(self, response):
        data = json.loads(response.body_as_unicode())
        for office in data['OfficeList']:
            result = {
                'company-id': office['OfficeId'],
                'url': office['DetailUrl'],
                'lat': office['Latitude'],
                'lon': office['Longitude'],
                'working_time': {'#content': office['TimeWork'], '@lang': "ru"},
            }
            self.log(result)



