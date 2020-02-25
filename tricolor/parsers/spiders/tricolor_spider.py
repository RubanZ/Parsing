# coding=utf-8

import json
import time
from collections import OrderedDict
import re
import scrapy
import sys



def safe_extract(item, path):
    result = ""
    try:
        pathes = path.split("/")
        for p in pathes:
            if isinstance(item, list):
                item = item[int(p)]
            else:
                item = item[p]
        result = item
        if result is None:
            result = ""
    except:
        return ""
    return result


class TricolorSpider(scrapy.Spider):
    name = 'tricolor_spider'
    start_urls = [
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=14&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=17&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=18&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=19&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=20&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=21&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=22&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=23&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=24&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=25&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=26&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=27&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=28&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=29&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=30&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=31&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=32&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=34&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=35&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=36&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=37&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=38&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=39&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=40&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=41&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=42&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=43&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=44&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=45&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=46&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=47&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=48&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=49&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=50&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=51&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=52&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=53&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=55&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=56&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=59&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=60&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=61&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=62&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=63&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=64&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=66&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=67&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=68&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=69&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=70&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=71&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=72&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=73&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=74&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=76&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=80&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=82&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=84&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=85&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=87&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=88&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=90&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=105&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=107&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=113&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=114&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=115&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=116&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55',
        'https://www.tricolor.tv/ajax/exchange/getPoints.php?geo_id=117&geo_type=region&page=offices&data_iblock_p=54&data_iblock_t=55'
    ]
    actualization_date = str(int(time.time()))
    iter = 1
    rubric_ids = ["184107403", "184107777", "184107389", "184107613"]
    gen_name = u"Триколор ТВ"
    gen_url = "https://www.tricolor.tv"

    def parse(self, response):
        html = response.body_as_unicode()
        json_obj = json.loads(html)
        for obj in json_obj:
            ids = obj["id"]
            yield scrapy.Request("https://www.tricolor.tv/ajax/exchange/getPointInfo.php?id%5B%5D="+ids+"&data_iblock_p=54", self.parse_office,meta = {"coords":obj["coords"]})

    def parse_office(self, response):
        html = response.body_as_unicode()
        json_obj = json.loads(html)
        coords= response.meta["coords"]
        lat,lon = coords[0],coords[1]
        address = json_obj["address"]
        work_time = ", ".join(json_obj["times"]).lower()
        name_other = json_obj["title"]

        url = ""
        if len(json_obj["website"])>0:
            url = "https://"+json_obj["website"][0]

        name = self.gen_name
        phone = ", ".join(json_obj["phones"])

        result = OrderedDict()
        result["company-id"] = str(self.iter)
        result["name"] = {'#content': name, '@lang': "ru"}
        result["name_other"] = {'#content': name_other, '@lang': "ru"}
        result["rubric_id"] = self.rubric_ids
        result["country"] = {'#content': u"Россия", '@lang': "ru"}
        result["address"] = {'#content': address, '@lang': "ru"}
        result["actualization_date"] = self.actualization_date
        if url!="":
            result["url"] = url

        if lat is not None:
            result["lat"] = lat
        if lon is not None:
            result["lon"] = lon

        result["working_time"] = {'#content': work_time, '@lang': "ru"}
        result["phone"] = [{'number': i, 'add_number': "", "type": "phone"} for i in phone.split(", ")]

        self.iter += 1

        yield result


# process = CrawlerProcess({
#     'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
#     'LOG_LEVEL': 'ERROR',
#     'FEED_EXPORT_ENCODING': 'utf-8',
#     'FEED_URI': 'stdout:',
#     'FEED_FORMAT': "jl"
# })
#
# process.crawl(TricolorSpider)
# process.start()
