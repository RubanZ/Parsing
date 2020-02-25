# coding=utf-8
import json
import re
import sys
from time import time

import bs4
import requests
from lxml import etree

main_country = u'Türkiye'
lang = 'tr'
main_host = 'https://www.incideri.com/'
main_name = u'İnci'

main_phones = ['+90 850 222 74 63']

add_urls = ['https://www.instagram.com/incideri/', 'https://www.facebook.com/incideri', 'https://twitter.com/incideri']

rubrics = ['184107941', '184107943']

xml = etree.Element('companies')


def print_json(id, o_name, addr, phones, lat, lon, wh=u'', emails='', addr_add='', url=''):
    out = {'company-id': str(id), 'rubric_id': rubrics, 'add_url': []}

    for a in add_urls:
        if a:
            out['add_url'].append(a)

    if url:
        out['add_url'].append(url)

    out['url'] = main_host

    out['name'] = {'#content': main_name, '@lang': lang}

    if o_name:
        out['name_other'] = {'#content': o_name, '@lang': lang}

    out['address'] = {'#content': addr, '@lang': lang}

    if addr_add:
        out['address_add'] = {'#content': addr_add, '@lang': lang}

    out['country'] = {'#content': main_country, '@lang': lang}

    out['phone'] = []

    for p in main_phones + phones:  # !!
        if p:
            out['phone'].append({'number': p, 'add_number': '', 'type': 'phone'})

    out['email'] = emails
    
    out['working_time'] = {'#content': wh, '@lang': lang}

    out.update({'lat': lat, 'lon': lon})

    out['actualization_date'] = str(int(time()))

    sys.stdout.write(json.dumps(out, ensure_ascii=False, sort_keys=True).encode('utf-8') + '\n')


def normalize_address(address):
    address = re.sub(
        u'(\s(mahalle\s|mahallesi\s|mah\s|mh\s|mah\.|mh\.|cadde\s|caddesi\s|cad\s|cad\.|cd\.|sokak\s|sokağı\s|sok\.|sk\.))\s?(\w)',
        '\g<1>, \g<3>', address, flags=re.IGNORECASE | re.UNICODE)
    address = re.sub('\s,', ',', address)

    address = re.sub('(\w)\.(\w)', '\g<1>. \g<2>', address, flags=re.UNICODE)

    address = ' '.join(address.split()).title().strip()

    address = re.sub('(No?\s?:\s?[\d\s\-/\w]+?)(\s([^\W\d][^\W\d])+)', '\g<1>,\g<2>', address,
                     flags=re.UNICODE)  # comma after No:...
    address = re.sub('([^\d\s:][^\d\s])(\s?//?\s?)', '\g<1>, ', address)

    address = re.sub('\s+', ' ', address)
    
    address = re.sub(', Turkey \d*', '', address)

    return address


def normalize_phone(phone):
    if not phone:
        return None

    phone = phone.strip()
    if not phone or phone == '-':
        return None

    phone = re.sub('\D', '', phone)
    phone = re.sub('^0', '', phone)
    phone = re.sub('^90', '', phone)

    country_code = '+90'
    if len(phone) == 10:
        code, number = phone[:3], phone[3:]
        number = number[:3] + '-' + number[3:5] + '-' + number[-2:]
        phone = country_code + ' (' + code + ') ' + number
        return phone


if __name__ == '__main__':
    url = 'https://www.incideri.com/magazalarimiz'

    r = requests.get(url)

    h = bs4.BeautifulSoup(r.text.replace("'", "\'"), 'html.parser')

    addresses = []
    count = 0
    stores = h.select('.pro-stores-list > li > h2 > a')

    for store in stores:
        data = store['data-info']
        try:
            store = json.loads(data)
        except ValueError:
            string = u'{"id":"5047","order_no":null,"item_id":"1815733","name":"Nişantaşı","address":"Teşvikiye Cad No:12 Kat:2 Mağ. No:310 Nişantaşı Citys Şişli İstanbul","phone":"0 212 373 25 80","map_link":null,"city_id":"34","latitude":"41.051137","longitude":"28.992798","status":"2","shop_code":"M060","shop_title":"Nişantaşı","ca_shop_type":null,"district":null,"shop_logo":null,"working_hours":null,"country":null,"postcode":null,"is_featured":null}'
            store = json.loads(string)
        address = store['address']
        address = normalize_address(address)

        name = store['name']
        name = u'{} {}'.format(main_name, name)

        lat, lon = store['latitude'], store['longitude']

        addresses.append(address)
        count += 1
        print_json(count, name, address, [], lat, lon)
