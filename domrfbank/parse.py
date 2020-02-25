# coding=utf-8
import json
import os
import re
import sys
import traceback
from functools import partial
from multiprocessing import Lock
from multiprocessing.pool import ThreadPool
from time import sleep, time

import requests
from argparse import ArgumentParser

lock = Lock()
requests.urllib3.disable_warnings()

if 'pydevd' in sys.modules or 'debug' in os.environ:
    os.environ['http_proxy'] = 'socks5://localhost:9050'
    os.environ['https_proxy'] = 'socks5://localhost:9050'
    sys.stderr.write(requests.get('https://httpbin.org/ip').text + '\n')


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


main_country = u'Россия'
lang = 'ru'
main_host = 'https://domrfbank.ru'
main_name = u'Дом.рф'
count = 1
add_urls = []

email = ''

rubrics = []

main_phones = ['8 (800) 775-86-86']


def print_json(id, o_name, addr, phones, lat, lon, wh='', emails='', addr_add='', url=''):
    out = {'company-id': str(id), 'rubric_id': rubrics, 'add_url': []}

    for a in add_urls:
        if a:
            out['add_url'].append(a)

    if url:
        out['add_url'].append(url)

    out['url'] = main_host

    out['name'] = {'#content': main_name, '@lang': 'ru'}

    if o_name:
        out['name-other'] = {'#content': o_name, '@lang': 'ru'}

    out['address'] = {'#content': addr, '@lang': lang}

    if addr_add:
        out['address_add'] = {'#content': addr_add, '@lang': lang}

    out['country'] = {'#content': main_country, '@lang': lang}

    out['phone'] = []

    for p in main_phones:
        out['phone'].append({'number': p, 'add_number': '', 'type': 'phone'})

    for p in phones:
        out['phone'].append({'number': p['p'], 'add_number': p['a'], 'type': 'phone'})

    out['email'] = emails

    out['working_time'] = {'#content': wh, '@lang': lang}

    out.update({'lat': lat, 'lon': lon})

    out['actualization_date'] = str(int(time()))

    sys.stdout.write(json.dumps(out, ensure_ascii=False, sort_keys=True).encode('utf-8') + '\n')


def anti_quotes(s):
    s = s.replace('"', '')
    s = s.replace('<<', '')
    s = s.replace('>>', '')
    s = s.replace(u'«', '')
    s = s.replace(u'»', '')
    s = s.replace(u'“', '')
    s = s.replace(u'”', '')
    s = s.replace('&quot;', '')
    return s


def read_arguments():
    argp = ArgumentParser()
    argp.add_argument('--type', required=True, choices=['offices', 'atms'])
    args = argp.parse_args()
    return args


if __name__ == '__main__':
    args = read_arguments()

    if args.type == 'offices':
        main_name = u'Банк ДOM.РФ'
        rubrics = ['184105398']
    else:
        main_name = u'Банк ДOM.РФ, банкомат'
        rubrics = ['184105402']

    r = req('https://domrfbank.ru/local/ajax/offices.map.php')

    data = r.json()

    addresses = []

    if args.type == 'offices':
        print_json(count, u'Банк ДOM.РФ, Частное банковское обслуживание', u'г. Мосвка, 1-й Монетчиковский переулок, дом 3, строение 1', [], 55.732279, 37.628702, u'ПН-ПТ: С 9:00 до 20:00')
    for i in data['data']['pointsList']:
        if args.type == 'atms' and i['type']['atm']['type'] or args.type == 'offices' and i['type']['office']['type']:
            name = None
            if args.type == 'offices':
                name = u'{}, {}'.format(main_name, i['info']['title'])
                name = anti_quotes(name)

            address = i['info']['address']['full_address']
            address = re.sub('\d{4,}, ', '', address)

            wh = i['info']['worktime']['individuals']
            wh = re.sub(' ?<br>', ', ', wh)
            wh = re.sub(u',[^,]+выходн.+', '', wh)
            wh = re.sub(u' без перерыва', '', wh)

            lat = i['geo']['coords']['lat']
            lon = i['geo']['coords']['lng']

            addresses.append(address)
            if args.type == 'offices':
                count += 1
                print_json(count, name, address, [], lat, lon, wh)
            else:
                print_json(count, name, address, [], lat, lon, wh)
                count += 1