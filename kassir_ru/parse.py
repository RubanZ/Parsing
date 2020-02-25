# coding=utf-8
import json
import re
import sys
import traceback
from time import sleep, time

import bs4
import requests
from lxml import etree

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


main_country = u'Россия'
lang = 'ru'
main_host = 'https://kassir.ru/'
main_name = u'Kassir.ru'

add_urls = u''''''.split('\n')

email = ''

rubrics = ['184105870']

main_phones = []

xml = etree.Element('companies')


def addXML(id, o_name, addr, phones, lat, lon, wh=None, email=None, url=None):
    company = etree.Element('company')
    etree.SubElement(company, 'company-id').text = str(id)

    for rubric in rubrics:
        etree.SubElement(company, 'rubric-id').text = rubric

    etree.SubElement(company, 'url').text = main_host

    for a in add_urls:
        if a:
            etree.SubElement(company, 'add-url').text = a

    etree.SubElement(company, 'add-url').text = url

    name = etree.SubElement(company, 'name')
    name.text = main_name
    name.set('lang', lang)

    if o_name:
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
            phone = etree.SubElement(company, 'phone')
            etree.SubElement(phone, 'ext')
            etree.SubElement(phone, 'type').text = 'phone'
            etree.SubElement(phone, 'number').text = ph
            etree.SubElement(phone, 'info')

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
    if len(phone) > 10:
        phone = re.sub('^8', '', phone)
    phone = re.sub('^{}'.format(re.sub('\D', '', country_code)), '', phone)

    phone = phone[:10]

    if len(phone) == 10:
        code, number = phone[:3], phone[3:]
        number = number[:3] + '-' + number[3:5] + '-' + number[-2:]
        phone = country_code + ' (' + code + ') ' + number
        return phone
    elif len(phone) == 6:
        return phone
    else:
        return None


def get_phones(s):
    phone = re.split('([,;]|[^);,\-\s] 8\s?\(|\+7| \()', s)
    for p in phone:
        p = normalize_phone(p)
        if p:
            yield p


def anti_quotes(s):
    s = s.replace('"', '')
    s = s.replace('<<', '')
    s = s.replace('>>', '')
    s = s.replace(u'«', '')
    s = s.replace(u'»', '')
    s = s.replace(u'“', '')
    s = s.replace(u'”', '')
    return s


if __name__ == '__main__':
    r = req('https://msk.kassir.ru/openapi/city?callback')
    text = r.text
    text = re.sub('^\(', '', text)
    text = re.sub('\);$', '', text)

    h = bs4.BeautifulSoup(json.loads(text)['html'], 'lxml')

    cities = h.select('.cities li a')

    addresses = []
    for city in cities:
        city_name = city.text.strip()

        # if city_name != u'Казань':
        #     continue  # TODO

        city_href = city['href'].split('?')[0].strip('/')

        url = '{}/biletnye-kassy'.format(city_href)

        try:
            r = req(url)
            h = bs4.BeautifulSoup(r.text, 'lxml')

            p = h.select_one('.phone')
            if p:
                p = p.text.strip()
                p = normalize_phone(p)
                main_phones = [p]
            else:
                main_phones = []
            print(r.text.encode('utf-8'))
            d = re.search('cashbox_list = ({.*?}),$', r.text, flags=re.M).group(1)
            
            d = json.loads(d)

            for item in d.values():
                address = item['hintContent']
                lat, lon = item['points']

                tr = h.find(lambda t: t and t.name == 'tr' and 'js-cashbox' in t.get('class', '') and address in t.text)

                tds = tr.find_all('td')

                try:
                    name, metro, address, pay, phone, wh = [td.get_text(strip=True, separator=' ') for td in tds]
                except:
                    #print([td.get_text(strip=True, separator=' ') for td in tds])
                    name, address, pay, phone, wh = [td.get_text(strip=True, separator=' ') for td in tds]

                if any(x in name.lower() for x in [u'партнер', u'авиакасса', u'info']):
                    continue

                if not (u'кассир' in name.lower() or 'kassir' in name.lower()):
                    sys.stderr.write(u'{}\n'.format(name).encode('utf-8'))
                    continue

                name = re.sub('[()]', '', name)

                address = anti_quotes(address)
                address = address.replace(u' Схема проезда', '')
                address = re.sub(u'Россия,? ?', '', address)

                phones = []

                phone = re.split('[,;]', phone)
                for p in phone:
                    p = normalize_phone(p)
                    if p and p not in main_phones:
                        phones.append(p)

                sys.stderr.write(wh.encode('utf-8') + '\n')

                wh = wh.replace(u'ВНИМАНИЕ!!! Невозможно выкупить забронированные на сайте билеты ', '')
                wh = wh.replace(u'ВНИМАНИЕ!!! БИЛЕТЫ БЕЗ СЕРВИСНОГО СБОРА ', '')
                wh = wh.replace(u'ТЦ Ворошиловский, 1 этаж. ', '')
                wh = wh.replace(u'Нагорный Дворец. ', '')
                wh = re.sub(u'[.,]\s(?!пятница|суббота|воскресенье|выходные|без|ежедневно|-|с|сб|вс|пт|пн|\d\d|перерыв|обед).+', '',
                            wh, flags=re.I | re.U)
                wh = re.sub(u' дополнительно.+', '', wh, flags=re.I | re.U)
                wh = re.sub(u' 1-й вагон.+', '', wh, flags=re.I | re.U)
                wh = re.sub(u'сб.+выходной', '', wh, flags=re.I | re.U)
                wh = re.sub(u'воскресенье.+выходной', '', wh, flags=re.I | re.U)

                sys.stderr.write(wh.encode('utf-8') + '\n\n')

                addresses.append(address)
                addXML(addresses.count(address), name, address, phones, lat, lon, wh=wh, url=city_href)
        except:
            traceback.print_exc()
            sys.stderr.write(url + '\n')

    x = etree.tounicode(xml, pretty_print=True)
    print("<?xml version='1.0' encoding='utf-8'?>")
    print(x.encode('utf-8'))
