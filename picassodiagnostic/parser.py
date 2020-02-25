# coding=utf-8

import json
import requests
from lxml import html
from time import time
import sys
import re

count = 0
rubric_id = ['184106106']

def print_data(companyid, name, city, address, coordinates, country, url, phone, working_time):
    array_phone = ''
    if phone != "":

        array_phone = u"["
        for p in phone:
            array_phone += u"{\"number\": \"" + p + u"\", \"type\": \"phone\"},"
        array_phone = array_phone[:-1]
        array_phone += u']'
    address = address.replace(u"Омск, ", u"")
    address = address.replace(u", 'БЦ на Вокзальной'", u"")
    address = address.replace(u"ТЦ 'Маяк Молл' этаж 5", u"ТЦ 'Маяк Молл', этаж 5")
    address = address.replace(u"Красный проспект, д. 182, ТЦ \"Европа\", этаж 3, офис 3/14", u"Красный проспект, д. 182, ТЦ 'Европа', этаж 3, офис 3/14")
    address = address.replace(u"м. Озерки, ТК 'Вояж', проспект Энгельса, д. 124, вход 3, этаж 2", u"проспект Энгельса, д. 124")
    address = address.replace(u", отдельный вход со двора", u"")
    address = re.sub(u' \(.*\)', u'', address)
    working_time = working_time.replace(u"Вс выходной", u"")
    addr = city + ', '
    addr += address
    
    result = {
        'name': {
            '@lang': 'ru',
            '#content': u'Пикассо'
        },
        'address': {
            '@lang': 'ru',
            '#content': re.sub(u"БЦ '.*', |ТЦ '.*', |ТК '.*', |ТРК '.*', |ТРЦ '.*', |Универмаг '.*', ", u'', addr).replace('\'', '')
        },
        'lat': str(coordinates[0]),
        'lon': str(coordinates[1]),
        'country': {
            '@lang': 'ru',
            '#content': country
        },
        'actualization_date': int(time()),
        'phone': array_phone,
        'company-id': str(companyid),
        'url': 'https://picasso-diagnostic.ru/',
        'add_url': url,
        'working_time': {
            '@lang': 'ru',
            '#content': working_time.replace('<br/>', ' ')
        },
        'rubric_id': rubric_id

    }
    if (re.findall(u"БЦ '.*'|ТЦ '.*'|ТК '.*'|ТРК '.*'|ТРЦ '.*'|Универмаг '.*'", addr) != []):
        n = re.search(u"БЦ '.*'|ТЦ '.*'|ТК '.*'|ТРК '.*'|ТРЦ '.*'|Универмаг '.*'", addr)
        add = {
            'address_add': {
                '@lang': 'ru',
                '#content': n.group(0).replace('\'', '')
            }
        }
        result.update(add)
    return json.dumps(result, ensure_ascii=False).encode('utf-8')



if __name__ == "__main__":
    url_main = "https://picasso-diagnostic.ru"
    citys_get = requests.get(url_main,headers = {'Upgrade-Insecure-Requests' : '1 ','User - Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.3', 'Cache-Control': 'no-cache'})
    urls_city = html.fromstring(citys_get.content).xpath('//a[@class="links__link js-geolocation-link"]/@href')
    citys = html.fromstring(citys_get.content).xpath('//a[@class="links__link js-geolocation-link"]/text()')
    for id in range(len(urls_city)):
        upd = requests.get(url_main + urls_city[id], headers = {'Upgrade-Insecure-Requests' : '1 ','User - Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.3', 'Cache-Control': 'no-cache'}, allow_redirects = False)
        cookie = upd.cookies.get_dict()
        data = requests.get("https://picasso-diagnostic.ru/pts/map/?" + str(count), cookies=cookie, headers = {'Upgrade-Insecure-Requests' : '1 ','User - Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.3', 'Cache-Control': 'no-cache'})
        text = data.content.replace('\u00ab', '\'').replace('\u00bb', '\'').replace('\u0301', '')
        res = json.loads('{"data": ' + text.encode("utf-8") + '}')
        # req_phone = requests.get(res['data']['info'], cookies=cookie, headers = {'Upgrade-Insecure-Requests' : '1 ','User - Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.3', 'Cache-Control': 'no-cache'})
        # phone = html.fromstring(req_phone.content).xpath('//p[@class="contacts__param"]/a/text()')
        count+=1
        for r in res['data']:
            req_phone = requests.get(r['info'], cookies=cookie, headers = {'Upgrade-Insecure-Requests' : '1 ','User - Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.3', 'Cache-Control': 'no-cache'})
            phone = html.fromstring(req_phone.content).xpath('//p[@class="contacts__param"]/a/text()')
            print( print_data(r['id'],
                                r['district'][0]['label'],
                                citys[id],
                                r['address'],
                                r['coordinates'].split(','),
                                u'Россия',
                                r['info'],
                                phone,
                                r['schedule']
                                ))
            
