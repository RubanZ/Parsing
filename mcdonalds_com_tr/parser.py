# coding=utf-8
import re
import time
from HTMLParser import HTMLParser

import requests
from lxml import etree


def request(url, decode='utf-8', method='GET', headers={}, data={}, json={}):
    headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:44.0) Gecko/20100101 Firefox/44.0'})
    tries = 0
    while tries < 10:
        try:
            response = requests.request(method, url, headers=headers, data=data, json=json)
            response.encoding = decode
            return response
        except:
            tries += 1
            time.sleep(5)
    raise Exception(u'Ошибка соединения')


main_host = 'https://www.mcdonalds.com.tr'
main_country = u'Türkiye'
rubric = '184106386'

main_name = 'Mcdonald\'S'
main_phone = '444 62 62'

add_urls = ['https://www.facebook.com/McDonaldsTurkiye', 'https://www.instagram.com/mcdonaldsturkiye']

main_url = 'https://www.mcdonalds.com.tr/restaurants/getstores'

xml = etree.Element('companies')


def addXML(id, other_name, addr, lat, lon, wh, ph):
    company = etree.Element('company')
    etree.SubElement(company, 'company-id').text = id
    etree.SubElement(company, 'rubric-id').text = rubric

    etree.SubElement(company, 'url').text = main_host

    # for a in add_urls:
    #     etree.SubElement(company, 'add-url').text = a

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

    working_time = etree.SubElement(company, 'working-time')
    working_time.text = wh
    working_time.set('lang', 'tr')

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

    coordinates = etree.SubElement(company, 'coordinates')
    lt = etree.SubElement(coordinates, 'lat')
    lt.text = str(lat)
    ln = etree.SubElement(coordinates, 'lon')
    ln.text = str(lon)

    etree.SubElement(company, 'actualization-date').text = str(int(time.time()))

    xml.append(company)


def main():
    response = request(main_url, method='POST', headers={"Content-Type": "application/x-www-form-urlencoded"},  data='cityId=0&subcity=&avm=false&birthday=false&isDeliveryStore=false&open724=false&breakfast=false&mcdcafe=false')
    data = response.json()['data']

    for i in range(len(data)):
        d = data[i]
        name = u'{} {}'.format(main_name, d['STORE_NAME'])
        address = normalizeAddress(d['STORE_ADDRESS'])
        #address = u'{}, {}, {}'.format(address, d['Town'], d['City']).title()
        #address = address.replace(u' (Avrupa)', '').replace(u' (Anadolu)', '')

        lat = d['LATITUDE']
        lon = d['LONGITUDE']
        wh = u'her gün ' + str(d['STARTWORKTIME']['Hours']) + ':00 - ' + str(d['ENDWORKTIME']['Hours']) + ':00'
        # for w in d['WorkingHours']:
        #     wh.append(u'{} {}'.format(w['Name'], w['Value']).strip())

        # wh = ', '.join(wh)
        if wh == u'her gün 0:00 - 0:00':
            wh = u'24 saat'
        phone = normalizePhone(d['STORE_PHONE'])

        addXML(str(i + 1), name, address, lat, lon, wh, phone)

    x = etree.tounicode(xml, pretty_print=True)
    print("<?xml version='1.0' encoding='utf-8'?>")
    print(x.encode('utf-8'))


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
    address = re.sub('\s-$', '', address)

    address = ' '.join(address.split()).title().strip()

    return address


def normalizePhone(phone):
    if not phone or phone == '-':
        return None

    phone = re.sub('\D', '', phone)
    phone = re.sub('^0', '', phone)

    country_code = '+90'
    code, number = phone[:3], phone[3:]
    number = number[:3] + '-' + number[3:5] + '-' + number[-2:]
    phone = country_code + ' ' + code + ' ' + number
    return phone


if __name__ == '__main__':
    main()
