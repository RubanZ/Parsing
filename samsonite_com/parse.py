# coding=utf-8
import json
import re
import sys
import traceback
from time import sleep, time
from xml.etree.ElementTree import fromstring

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
main_host = 'http://www.samsonite.com.tr'
main_name = u'Samsonite'



email = ''

rubrics = ['184107955']

main_phones = []


def print_json(id, o_name, addr, phones, lat, lon, wh='', email='', address_add='', add_urls=''):
    out = {'company-id': str(id), 'rubric_id': rubrics, 'url': main_host}

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
        out['working_time'] = {'#content': wh, '@lang': lang}

    out.update({'lat': lat, 'lon': lon})

    out['actualization_date'] = str(int(time()))

    sys.stdout.write(json.dumps(out, ensure_ascii=False, sort_keys=True).encode('utf-8') + '\n')


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

    address = re.sub(',?\s?\(.+?\)', '', address)

    address = re.sub(r'(\s\w+),?\1', r'\1', address, flags=re.I | re.U)

    address = re.sub('( \w+) (\w+)$', r'\1, \2', address, flags=re.U)

    address = address.replace(',,', ',')

    address = re.sub('([a-z]) - ([a-z])', r'\1, \2', address, flags=re.I)

    address = re.sub(u'\s,', ', ', address)

    return address


if __name__ == '__main__':
    url = "https://www.samsonite.com.tr/stores/?format=json"
    r = req(url)
    myJson = json.loads(r.content)
    id = 0
    for item in myJson["results"]:
        add_urls = u'https://www.facebook.com/samsoniteofficial\nhttps://www.instagram.com/mysamsonite/\nhttps://twitter.com/MySamsonite\n'
        if item["store_hours"][0][0] == "00:00:00":
            wh = u'saat'
        else:
            wh = '10:00 - 22:00'
        print_json(id, item["name"], normalize_address(item["address"]), normalize_phone(item["phone_number"]), item["latitude"], item["longitude"], add_urls=add_urls+main_host+item["absolute_url"], wh=wh)
        id+= 1