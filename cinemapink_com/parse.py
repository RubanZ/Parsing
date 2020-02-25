# coding=utf-8
import json
import re
import sys
import traceback
from time import sleep, time

import bs4
import requests

requests.urllib3.disable_warnings()


def req(url, decode='utf-8', method='GET', headers={}, data=None, params=None):
    headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/62.0.3202.62 Safari/537.36'})
    tries = 0
    while tries < 10:
        try:
            resp = requests.request(method, url, headers=headers, timeout=60, data=data, params=params, verify=False)
            resp.encoding = decode
            return resp
        except Exception as e:
            sys.stderr.write('try {}\n'.format(tries))
            sys.stderr.write(u'{}\n'.format(traceback.format_exc()).encode('utf-8'))
            tries += 1
            sleep(5)
    raise Exception('Ошибка соединения')


main_country = u'Türkiye'
lang = 'tr'
main_host = 'http://www.cinemapink.com'
main_name = u'Cinemapink'

add_urls = u'''https://www.facebook.com/cinemapink/
https://twitter.com/CinemaPinktalks
https://www.instagram.com/cinemapink/'''.split('\n')

email = 'info@cinemapink.com'

rubrics = ['184105868']

main_phones = []


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

    out['email'] = email  #

    out['working_time'] = {'#content': wh, '@lang': lang}

    out.update({'lat': lat, 'lon': lon})

    out['actualization_date'] = str(int(time()))

    sys.stdout.write(json.dumps(out, ensure_ascii=False, sort_keys=True).encode('utf-8') + '\n')


def normalize_address(address):
    address = re.sub('(\w)\s?-(\s?\w)', '\\1, \\2', address, flags=re.U | re.I)

    address = re.sub(
        u'(\s(mahalle\s|mahallesi\s|mah\s|mh\s|mah\.|mh\.|cadde\s|caddesi\s|cad\s|cad\.|cd\.|sokak\s|sokağı\s|sok\.|sk\.))\s?(\w)',
        '\g<1>, \g<3>', address, flags=re.IGNORECASE | re.UNICODE)
    address = re.sub('\s,', ',', address)

    address = re.sub('(\w)\.(\w)', '\g<1>. \g<2>', address, flags=re.UNICODE)

    address = ' '.join(address.split()).title().strip()

    address = re.sub('(No?\s?:\s?[\d\s\-/\w]+?)(\s([^\W\d][^\W\d])+)', '\g<1>,\g<2>', address,
                     flags=re.UNICODE)  # comma after No:...
    address = re.sub('([^\d\s:][^\d\s])(\s?//?\s?)', '\g<1>, ', address)

    address = re.sub('\(.+?\)', '', address)

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
        number = number[:3] + ' ' + number[3:5] + ' ' + number[-2:]
        phone = country_code + ' ' + code + ' ' + number
        return phone


if __name__ == '__main__':
    url = 'http://www.cinemapink.com/'

    r = req(url)
    h = bs4.BeautifulSoup(r.text, 'html.parser')

    li = h.select_one('#collapsetree > li')
    items = li.select('ul > li > a')
    addresses = []
    count = 0
    del items[0]
    for i in items:
        u = 'http://www.cinemapink.com' + i['href']
        r = req(u)
        h = bs4.BeautifulSoup(r.text, 'html.parser')

        name = h.find(id='IBaslik').text.strip()
        name = u'Cinemapink {}'.format(name)

        data_addr = h.find(class_='SAdres').get_text(strip=True, separator='\n')
        data = data_addr.split('\n')

        if 'Dolby' in data_addr:
            data = data[2:]

        data = iter(data)

        address = next(data)
        address = normalize_address(address)

        phone = next(data).split('-')[0]
        phone = normalize_phone(phone)
        phones = [phone]

        lat = lon = None
        gmap = h.find('a', href=lambda h: h and 'google' in h)

        if gmap:
            gmap = gmap['href']
            s = re.search('ll=([\d.]+),([\d.]+)', gmap)
            if s:
                lat, lon = s.groups()
            else:
                #print(gmap)
                rg = req(gmap)
                s = re.search('\[([\d.]+),([\d.]+)\]', rg.text)
                #print(s.group(0))
                if s:
                    lat, lon = s.groups()
        if lat != None and lon != None:
            if float(lat) > 20.0 and float(lon) > 20.0:
                count+=1
                addresses.append(address)
                print_json(count, name, address, phones, lat, lon)
