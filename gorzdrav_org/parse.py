# coding=utf-8
import json
import re
import sys
import traceback
from argparse import ArgumentParser
from time import sleep, time

import requests

requests.urllib3.disable_warnings()
session = requests.session()


def req(url, decode='utf-8', method='GET', headers={}, data=None, params=None):
    headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/62.0.3202.62 Safari/537.36'})
    tries = 0
    while tries < 10:
        try:
            resp = session.request(method, url, headers=headers, timeout=60, data=data, params=params, verify=False)
            resp.encoding = decode
            return resp
        except Exception as e:
            sys.stderr.write('try {}\n'.format(tries))
            sys.stderr.write(u'{}\n'.format(traceback.format_exc()).encode('utf-8'))
            tries += 1
            sleep(5)
    raise Exception('Ошибка соединения')


main_country = u'Россия'
lang = 'ru'
main_host = 'https://gorzdrav.org'
main_name = u'ГорЗдрав'

add_urls = u''''''.split('\n')

email = ''

rubrics = ['184105932']

main_phones = []


def print_json(id, o_name, addr, phones, lat, lon, wh='', emails='', addr_add='', url=''):
    out = {'company-id': str(id), 'rubric_id': rubrics, 'url': [main_host], 'add_url': []}

    if url:
        out['add_url'].append(url)

    for a in add_urls:
        if a:
            out['add_url'].append(a)

    out['name'] = {'#content': main_name, '@lang': lang}

    if o_name:
        out['name_other'] = {'#content': o_name, '@lang': lang}

    out['address'] = {'#content': addr, '@lang': lang}

    if addr_add:
        out['address_add'] = {'#content': addr_add, '@lang': lang}

    out['country'] = {'#content': main_country, '@lang': lang}

    out['phone'] = []

    for p in main_phones:
        out['phone'].append({'number': p, 'add_number': '', 'type': 'phone', 'info': u'справочная'})

    for p in phones:
        out['phone'].append({'number': p, 'add_number': '', 'type': 'phone'})

    out['email'] = emails

    out['working_time'] = {'#content': wh, '@lang': lang}

    out.update({'lat': lat, 'lon': lon})

    out['actualization_date'] = str(int(time()))

    sys.stdout.write(json.dumps(out, ensure_ascii=False, sort_keys=True).encode('utf-8') + '\n')


def normalize_phone(phone, country_code='+7'):
    if re.search('8\s?\(800\)', phone):
        return phone

    if not phone:
        return None

    phone = phone.strip()
    if not phone or phone == '-':
        return None

    phone = re.sub('\D', '', phone)

    phone = re.sub('^0', '', phone)
    phone = re.sub('^8', '', phone)
    phone = re.sub('^{}'.format(re.sub('\D', '', country_code)), '', phone)

    phone = phone[:10]

    if len(phone) == 10:
        code, number = phone[:3], phone[3:]
        number = number[:3] + '-' + number[3:5] + '-' + number[-2:]
        phone = country_code + ' (' + code + ') ' + number
        return phone


def read_arguments():
    argp = ArgumentParser()
    argp.add_argument('--city', type=str, required=True, choices=['moscow', 'petersburg'])
    args = argp.parse_args()
    return args


if __name__ == '__main__':
    url = 'https://gorzdrav.org/_s/baseStore?code={}-gz'
    addresses = []
    count = 1
    cities = [
        [u'Москва', '7 (499) 653-62-77', '77'],
        [u'Санкт-Петербург', '+7 (812) 426-15-84', '78']
    ]

    args = read_arguments()

    if args.city == 'moscow':
        city, phone, gz = cities[0]
    elif args.city == 'petersburg':
        city, phone, gz = cities[1]

    main_phones = [phone]

    url_format = url.format(gz)
    r = req(url_format)

    r = req('https://gorzdrav.org/store-finder/all/')
    d = r.json()['data']

    names = ','.join([x['name'] for x in d])
    coords = {x['name']: [x['latitude'], x['longitude']] for x in d}

    r = req('https://gorzdrav.org/store-finder/names', data="names=" + names, method='post',
            headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})
    try:
        i = r.json()
    except Exception as e:
        raise e

    for a in i:
        n = a['name']

        lat, lon = coords[n]

        name = a['displayName']
        address = a['address']
        city = a['town']

        phone = a['phone']

        if city not in address:
            address = u'{}, {}'.format(city, address)

        if 'fullOpeningSchedule' in a:
            wh = a['fullOpeningSchedule']
            wh = re.sub(u'\s*(<br>|<b>|<\/b>)\s*', ',', wh, flags=re.U | re.I)
            wh = re.sub(u',,', u',', wh)
        else:
            wh = u'круглосуточно'
        addresses.append(address)
        print_json(count, name, address, [phone], lat, lon, wh, url='https://gorzdrav.org/apteki/' + n)
        count += 1 
        
