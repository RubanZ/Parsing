# coding=utf-8
import json
import re
import sys
import traceback
from HTMLParser import HTMLParser
from time import sleep, time

import requests
from lxml import etree

requests.urllib3.disable_warnings()
session = requests.session()


def req(url, decode='utf-8', method='GET', headers={}, data=None, params=None, proxy=None):
    headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/62.0.3202.62 Safari/537.36'})
    tries = 0
    while tries < 10:
        try:
            resp = session.request(method, url, headers=headers, timeout=60, data=data, params=params, verify=False,
                                   proxies=proxy)
            resp.encoding = decode
            if resp.text:
                return resp
            else:
                raise Exception('Empty response text')
        except Exception as e:
            sys.stderr.write('try {}\n'.format(tries))
            sys.stderr.write(u'{}\n'.format(traceback.format_exc()).encode('utf-8'))
            tries += 1
            sleep(5)
    raise Exception('Connection error')


main_country = u'Türkiye'
lang = 'tr'
main_host = 'https://www.lacoste.com.tr'
main_name = u'Lacoste'

add_urls = []

rubrics = ['184107943']

main_phones = []

xml = etree.Element('companies')


def addXML(id, o_name, addr, phones, lat, lon, wh, email, fax, url):
    company = etree.Element('company')
    etree.SubElement(company, 'company-id').text = str(id)

    for rubric in rubrics:
        etree.SubElement(company, 'rubric-id').text = rubric

    etree.SubElement(company, 'url').text = main_host

    # for a in add_urls:
    #     etree.SubElement(company, 'add-url').text = a

    # etree.SubElement(company, 'add-url').text = url

    name = etree.SubElement(company, 'name')
    name.text = main_name
    name.set('lang', lang)

    other_name = etree.SubElement(company, 'name-other')
    other_name.text = o_name
    other_name.set('lang', lang)

    country = etree.SubElement(company, 'country')
    country.text = main_country
    country.set('lang', lang)

    address = etree.SubElement(company, 'address')
    address.text = addr
    address.set('lang', lang)

    for mph in main_phones:
        phone = etree.SubElement(company, 'phone')
        etree.SubElement(phone, 'ext')
        etree.SubElement(phone, 'type').text = 'phone'
        etree.SubElement(phone, 'number').text = mph
        etree.SubElement(phone, 'info')

    for ph in phones:
        if ph:
            s = re.search(r'\s[(#]\s?(\d+)\)?', ph)
            ext = s.group(1) if s else None
            ph = ph.replace(s.group(0), '') if s else ph

            phone = etree.SubElement(company, 'phone')
            if ext:
                etree.SubElement(phone, 'ext').text = ext
            else:
                etree.SubElement(phone, 'ext')
            etree.SubElement(phone, 'type').text = 'phone'
            etree.SubElement(phone, 'number').text = ph
            etree.SubElement(phone, 'info')

    if fax:
        fx = etree.SubElement(company, 'phone')
        etree.SubElement(fx, 'ext')
        etree.SubElement(fx, 'type').text = 'fax'
        etree.SubElement(fx, 'number').text = fax
        etree.SubElement(fx, 'info')

    if email:
        etree.SubElement(company, 'email').text = email

    if wh:
        working_time = etree.SubElement(company, 'working-time')
        working_time.text = wh
        working_time.set('lang', lang)

    coordinates = etree.SubElement(company, 'coordinates')
    lt = etree.SubElement(coordinates, 'lat')
    lt.text = str(lat)
    ln = etree.SubElement(coordinates, 'lon')
    ln.text = str(lon)

    etree.SubElement(company, 'actualization-date').text = str(int(time()))

    xml.append(company)


def normalize_phone(phone, country_code='+7'):
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
        number = number[:3] + ' ' + number[3:5] + ' ' + number[-2:]
        phone = country_code + ' ' + code + ' ' + number
        return phone


def format_wh(wh):
    if not wh:
        return None

    day_names = {'1': u'Pazartesi', '2': u'Salı', '3': u'Çarşamba', '4': u'Perşembe', '5': u'Cuma', '6': u'Cumartesi',
                 '7': u'Pazar'}

    whs = wh.split(',')
    isOk = True
    t = whs[0]
    for w in whs:
        if w != t:
            isOk = False
    if not isOk:
        st = ''
        for w in range(len(whs)):
            st += day_names[str(w+1)] + ' ' + whs[w] + ', '
        st = st[:-1]
        st = st[:-1]
        return st
    else:
        return u'her gün ' + t

hp = HTMLParser()
def normalizeAddress(address):
    address = hp.unescape(address)
    address = re.sub(
        u'(\s(mahalle\s|mahallesi\s|mah\s|mh\s|mah\.|mh\.|cadde\s|caddesi\s|cad\s|cad\.|cd\.|sokak\s|sokağı\s|sok\.|sk\.))\s?(\w)',
        '\g<1>, \g<3>', address, flags=re.IGNORECASE | re.UNICODE)
    address = re.sub('\s,', ',', address)

    address = re.sub('(\w)\.(\w)', '\g<1>. \g<2>', address, flags=re.UNICODE)
    
    address = re.sub('/', ', ', address)
    address = re.sub(' ,', ',', address)
    address = re.sub(' \d\d\d\d\d', '', address)
    address = re.sub(', \d\d\d\d\d', '', address)
    address = re.sub(' -', ',', address)
    address = re.sub('\s-$', '', address)

    address = ' '.join(address.split()).title().strip()

    return address

if __name__ == '__main__': # 54.742113, 20.301198
    r = req('https://www.lacoste.com.tr/address/city/?retailstore__isnull=false&country=1', method='GET')
    data = r.json()
    count = 0
    addresses = []
    for city in data['results']:
        r2 = req('https://www.lacoste.com.tr/address/retail_store/?format=json&city=' + str(city['pk']), method='GET')
        data2 = r2.json()
        for item in data2['results']:
            wh = ''
            for w in item['store_hours']:
                wh += w[0][:-1][:-1][:-1] + " - " + w[1][:-1][:-1][:-1]
                wh += ','
            wh = wh[:-1]
            wh = format_wh(wh)
            email = ''
            phone = [normalize_phone(item['phone_number'], '+90')]
            count+=1
            address = item['address']
            print(address.encode('utf-8'))
            address = address.replace(u', Ankara', u'')
            address = address.replace(u', Adana', u'')
            address = address.replace(u', Antalya', u'')
            address = address.replace(u', Bursa', u'')
            address = address.replace(u', İstanbul', u'')
            address = address.replace(u',  İstanbul', u'')
            address = address.replace(u' – İstanbul', u'')
            address = address.replace(u', Türkiye', u'')
            address = address.replace(u', İzmir', u'')
            address = address.replace(u', Kayseri', u'')
            address = address.replace(u', Konya', u'')
            address = address.replace(u', Mersin', u'')
            address = address.replace(u', Muğla', u'')
            address = address.replace(u', Samsun', u'')
            address = address.replace(u', Trabzon', u'')
            address = normalizeAddress(address + ', ' + city['name'])
            addXML(count, item['name'], address, phone, item['latitude'], item['longitude'], wh, email, item['fax_phone_number'], 'https://www.lacoste.com.tr/' + item['absolute_url'])
        # if s['country'] != 'Russia':
        #     continue

        # name = s['name'].replace('&quot;', '"')

        # lat, lon = s['latitude'], s['longitude']

        # address = u'{}, {}'.format(s['city'], s['address'])

        # phone = s['phone']

        # fax = s['fax']

        # wh = s['hours']
        # wh = format_wh(wh)

        # email = s['email']

        # url = 'https://stores.lacoste.com/#{}'.format(i)

        # addresses.append(address)
        # addXML(addresses.count(address), name, address, [phone], lat, lon, wh, email, fax, url)

    x = etree.tounicode(xml, pretty_print=True)
    print("<?xml version='1.0' encoding='utf-8'?>")
    print(x.encode('utf-8'))
