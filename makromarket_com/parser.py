# coding=utf-8
import json
import re
import sys
import time
from multiprocessing.pool import ThreadPool

import requests
from lxml import etree
from lxml.html import fromstring, tostring


def request(url, decode='utf-8', method='GET', headers={}, data=None, json=None):
    # headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:44.0) Gecko/20100101 Firefox/44.0'})
    headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
    tries = 0
    while tries < 10:
        try:
            response = requests.request(method, url, headers=headers, data=data, json=json, timeout=10)
            response.encoding = decode
            return response
        except Exception as e:
            sys.stderr.write('try {}\n'.format(tries))
            sys.stderr.write('{}\n'.format(e))
            tries += 1
            time.sleep(5)
    raise Exception('Ошибка соединения')


main_country = u'Türkiye'
main_host = 'http://www.makromarket.com.tr'

main_name = u'Makro Market'
main_phone = ''

add_urls = []

rubrics = ['184108075', '184108079']

main_url = 'http://www.makromarket.com.tr/Magazalar'

xml = etree.Element('companies')


def addXML(id, other_name, addr, lat, lon, ph, email):
    company = etree.Element('company')
    etree.SubElement(company, 'company-id').text = id

    for rubric in rubrics:
        etree.SubElement(company, 'rubric-id').text = rubric

    etree.SubElement(company, 'url').text = main_host

    for a in add_urls:
        etree.SubElement(company, 'add-url').text = a

    name = etree.SubElement(company, 'name')
    name.text = main_name
    name.set('lang', 'tr')

    name_other = etree.SubElement(company, 'name-other')
    name_other.text = other_name
    name_other.set('lang', 'tr')

    country = etree.SubElement(company, 'country')
    country.text = main_country
    country.set('lang', 'tr')

    address = etree.SubElement(company, 'address')
    address.text = addr
    address.set('lang', 'tr')

    if main_phone:
        phone = etree.SubElement(company, 'phone')
        etree.SubElement(phone, 'ext')
        etree.SubElement(phone, 'type').text = 'phone'
        etree.SubElement(phone, 'number').text = main_phone
        etree.SubElement(phone, 'info')

    if ph:
        phone = etree.SubElement(company, 'phone')
        etree.SubElement(phone, 'ext')
        etree.SubElement(phone, 'type').text = 'phone'
        etree.SubElement(phone, 'number').text = ph
        etree.SubElement(phone, 'info')

    if email:
        etree.SubElement(company, 'email').text = email

    coordinates = etree.SubElement(company, 'coordinates')
    lt = etree.SubElement(coordinates, 'lat')
    lt.text = str(lat)
    ln = etree.SubElement(coordinates, 'lon')
    ln.text = str(lon)

    etree.SubElement(company, 'actualization-date').text = str(int(time.time()))

    xml.append(company)


def debug(*s):
    s = ' '.join([str(x) for x in s])
    sys.stderr.write(s)
    sys.stderr.write('\n')


data = []


def main():
    response = request(main_url)
    html = response.text
    html = fromstring(html)

    cities = [unicode(s) for s in html.xpath('//ul[@id="one"]/li/text()')]

    def error(err):
        debug(err)

    pool = ThreadPool(16)
    pool.map(grab, cities)
    pool.close()
    pool.join()

    # for city in cities:
    #     grab(city)

    i = 0
    for d in data:
        i += 1
        addXML(str(i), d['name'], d['address'], d['lat'], d['lon'], d['phone'], d['email'])

    x = etree.tounicode(xml, pretty_print=True)
    print("<?xml version='1.0' encoding='utf-8'?>")
    print(x.encode('utf-8'))


def grab(city):
    global data
    response = request(u'{}/{}'.format(main_url, city))
    html = response.text
    html = fromstring(html)
    shops = html.xpath('//div[@class="magazalar_new_content"]')

    entries = []
    for shop in shops:
        shop = fromstring(tostring(shop))

        name = shop.xpath('//p')[0].text.title()
        name = u'{} {}'.format(main_name, name)
        name = name.replace('i', u'ı')

        lat = shop.xpath('//div[@id="x"]')[0].text
        lon = shop.xpath('//div[@id="y"]')[0].text

        url = u'{}{}'.format(main_host, shop.xpath('//a')[1].attrib['href'])

        if lat and lon:
            lat = lat.replace(',', '.')
            lon = lon.replace(',', '.')
        else:
            debug('Has no coordinates:', url.replace('Index', 'Harita'))

        response = request(url)
        info = response.text
        info = fromstring(info)

        address = info.xpath('//tr[2]/td[2]')[0].text
        city_town = info.xpath('//tr[3]/td[2]')[0].text
        address = u'{}, {}'.format(address.strip(), ', '.join(reversed(city_town.split(' - '))))
        address = normalizeAddress(address)
        address = address.replace('i', u'ı')

        phone = info.xpath('//tr[4]/td[2]')[0].text
        phone = normalizePhone(phone)

        email = info.xpath('//tr[6]/td[2]')[0].text

        entry = dict(
            name=name,
            address=address,
            phone=phone,
            email=email,
            lat=lat,
            lon=lon
        )

        debug(json.dumps(entry))

        data.append(entry)


def normalizeAddress(address):
    # address = hp.unescape(address)
    address = re.sub(
        u'(\s(mahalle\s|mahallesi\s|mah\s|mh\s|mah\.|mh\.|cadde\s|caddesi\s|cad\s|cad\.|cd\.|sokak\s|sokağı\s|sok\.|sk\.))\s?(\w)',
        '\g<1>, \g<3>', address, flags=re.IGNORECASE | re.UNICODE)
    address = re.sub('\s,', ',', address)

    # address = re.sub('\s-$', '', address)
    address = ' '.join(address.split()).title().strip()

    address = re.sub('(No?:\s?[\d\s\-/\w]+?)(\s?([^\W\d][^\W\d])+)', '\g<1>,\g<2>', address,
                     flags=re.UNICODE)  # comma after No:...
    address = re.sub('([^\d\s:][^\d\s])(\s?//?\s?)', '\g<1>, ', address)

    return address


def normalizePhone(phone):
    phone = phone.strip()

    phone = re.sub('\D', '', phone)
    phone = re.sub('^0', '', phone)
    phone = re.sub('^90', '', phone)

    if not phone or phone == '-':
        return None

    country_code = '+90'
    code, number = phone[:3], phone[3:]
    number = number[:3] + '-' + number[3:5] + '-' + number[-2:]
    phone = country_code + ' (' + code + ') ' + number

    return phone


if __name__ == '__main__':
    main()
