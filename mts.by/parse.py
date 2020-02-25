# -*- coding: UTF-8 -*- 
import demjson
import json
import re
from time import sleep, time
import requests  
import sys        

rubriks = ["184107783","184107789"]
main_host="https://www.mts.by/"
main_name= u'МТС'
lang = u'ru'
main_country = u'Беларусь'

def print_json(id, o_name, addr, phones, lat, lon, wh='', email='', address_add='', add_urls=''):
    out = {}
    out['company-id'] = id
    out['rubric_id'] = rubriks
    out['url'] = main_host

    if add_urls:
        out['add_url'] = add_urls.split('\n')

    out['name'] = {'#content': main_name, '@lang': lang}

    if o_name:
        out['name_other'] = {'#content': o_name, '@lang': lang}

    out['address'] = {'#content': addr, '@lang': lang}

    if address_add:
        out['address_add'] = {'#content': address_add, '@lang': lang}

    out['country'] = {'#content': main_country, '@lang': lang}

    out['phone'] = {'number': phones, 'add_number': '', 'type': 'phone'}

    out['email'] = email

    if wh:
        wh = wh.replace(u'\t', ' ')
        wh = wh.replace(u'–', u'-')
        wh = re.sub(u'(\S обед:.{,1}\d\d.\d\d-\d\d.\d\d)', u'', wh)
        wh = re.sub(u'(\S{0,} обед.{,1}\d\d.\d\d-\d\d.\d\d)', u'', wh)
        wh = wh.replace(u', вс., пн.: вых.', '')
        wh = wh.replace(u'; вс., пн.: вых.', '')
        wh = wh.replace(u'; пн.: вых.', '')
        wh = wh.replace(u', пн.: вых.', '')
        wh = wh.replace(u';  пн.:вых.', '')
        wh = wh.replace(u'; сб.- вс.: вых.', '')
        wh = wh.replace(u', вс.: вых.', '')
        wh = wh.replace(u', сб.-вс.: вых.', '')
        wh = wh.replace(u', чт.,пн.: вых.', '')
        wh = wh.replace(u', пн.,вс.: вых.', '')
        wh = wh.replace(u'; пн.:вых.', '')
        wh = wh.replace(u', вых.: вс, пн.', '')
        wh = wh.replace(u'; вс.-пн.: вых.', '')
        wh = wh.replace(u'; вс.: вых.', '')
        wh = wh.replace(u'; вс..: вых.', '')
        wh = wh.replace(u', вс.пн.: вых.', '')
        wh = wh.replace(u'; сб.,вс.: вых.', '')
        wh = wh.replace(u', сб.- вс: вых.', '')
        wh = wh.replace(u';  сб.- вс.: вых.', '')
        wh = wh.replace(u', вс.- пн.: вых.', '')
        wh = wh.replace(u', сб.вс.:вых.', '')
        wh = wh.replace(u', вс.-пн.: вых.', '')
        wh = wh.replace(u', сб.: вых.', '')
        wh = wh.replace(u',    вс., пн: вых.', '')
        wh = wh.replace(u', сб.- вс.: вых.', '')
        wh = wh.replace(u', сб.,вс.:вых.', '')
        wh = wh.replace(u',        вс.:вых.', '')
        wh = wh.replace(u'; вых.: 1-й вт. месяца', '')
        wh = wh.replace(u'; вс: вых.', '')
        wh = wh.replace(u',  вс.: вых.', '')
        wh = wh.replace(u'пн., вт.: вых. ', '')
        wh = wh.replace(u', пн.-вс.: вых.', '')
        wh = wh.replace(u' вс.,пн.: вых.', '')
        wh = wh.replace(u', вых.: пн.', '')
        wh = wh.replace(u', сб. вс.: вых.', '')
        wh = wh.replace(u', сб.:вых.', '')
        wh = wh.replace(u'с 10:00-21:00 без обеда и выходных', u'ежедневно с 10:00-21:00')
        wh = wh.replace(u', обед с 14:00 до 15:00.', '')
        wh = wh.replace(u', обед 13.00-14.00', '')
        wh = wh.replace(u', (обед 14:00-14:30)', '')
        wh = wh.replace(u' (обед 14:00-14:30)', '')
        wh = wh.replace(u', перерыв 14:00-14:45', '')
        wh = wh.replace(u',  перерывы: 13.00-13.20, 17.00-17.20', '')
        wh = wh.replace(u', перерывы: 13.00-13.20, 16.00-16.20', '')
        wh = wh.replace(u' (перерыв 11:00-11:20, 15:00-15:20, 18:00-18:20)', '')
        wh = wh.replace(u', выходной 2-ой понедельник месяца', '')
        wh = wh.replace(u', перерыв: 14.00-14.20', '')
        wh = wh.replace(u'. Режим работы 01.01.2019 с 12:00 до 22:00', '')
        wh = wh.replace(u'пн: выходной,', '')
        wh = wh.replace(u', перерыв 14:00-14:45', '')
        wh = wh.replace(u', перерыв пн.-пт.: 14.00-14.20', '')
        wh = wh.replace(u'; перерыв: 11.20-11.40, 13.30-14.00, 16.20-16.40', '')
        wh = wh.replace(u', обед с 14:00 до 15:00', '')
        wh = wh.replace(u'. Обед: 13.00-14.00', '')
        wh = wh.replace(u'; сб.-вс.: вых.', '')
        wh = wh.replace(u', вс.: вых', '')
        wh = wh.replace(u' , пн.: вых', '')
        out['working_time'] = {'#content': wh, '@lang': lang}

    out.update({'lat': float(lat), 'lon': float(lon)})

    out['actualization_date'] = str(int(time()))

    sys.stdout.write(json.dumps(out, ensure_ascii=False, sort_keys=True).encode('utf-8') + '\n')



def GetFeeds():
    url="https://www.mts.by/help/mobilnaya-svyaz/obsluzhivanie-abonentov/salony-svyazi/"
    r = requests.get(url)
    string = re.search(r'var citiesAll = (\[\s*\{(\s\S*){1,});\s*var cities = citiesAll;', r.text).group(1)
    off_json = demjson.decode(string.encode('utf-8'))
    ids = 0
    for item in off_json:
        ids+=1
        print_json(ids, "", item['city'] + ", " + item['address'], item['phone'], item['center'][0], item['center'][1], item['time'])

        
    
   

GetFeeds()
        
