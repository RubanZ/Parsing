# coding=utf-8
import re
import sys
import traceback
from time import sleep, time
import json
import bs4
import requests
from lxml.html import fromstring
from lxml.html import tostring
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


main_country = u'Россия'
lang = 'ru'
main_host = 'https://www.prachka.com'
main_name = u'Prachka.com'

add_urls = []

rubrics = ['184108217']

main_phones = []

xml = etree.Element('companies')


def addXML(id, o_name, addr, ph, lat, lon, wh, url):
    company = etree.Element('company')
    etree.SubElement(company, 'company-id').text = str(id)

    for rubric in rubrics:
        etree.SubElement(company, 'rubric-id').text = rubric

    etree.SubElement(company, 'url').text = main_host

    for a in add_urls:
        etree.SubElement(company, 'add-url').text = a

    if url:
        etree.SubElement(company, 'add-url').text = url

    name = etree.SubElement(company, 'name')
    name.text = main_name
    name.set('lang', lang)

    # other_name = etree.SubElement(company, 'name-other')
    # other_name.text = o_name
    # other_name.set('lang', lang)

    country = etree.SubElement(company, 'country')
    country.text = main_country
    country.set('lang', lang)

    address = etree.SubElement(company, 'address')
    address.text = addr
    address.set('lang', lang)

    if ph:
        phone = etree.SubElement(company, 'phone')
        etree.SubElement(phone, 'ext')
        etree.SubElement(phone, 'type').text = 'phone'
        etree.SubElement(phone, 'number').text = ph
        etree.SubElement(phone, 'info')

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
        phone = country_code + ' (' + code + ') ' + number
        return phone

def getLanLon(context):
    context = context.replace(' ', '+')
    res2 = requests.get('https://geocode-maps.yandex.ru/1.x/?format=json&apikey=dcd843d2-061c-4e13-b126-6c4e6de0e956&geocode=' + context.encode('utf-8'))
    #print(res2.text.encode('utf-8'))
    json_ya = json.loads(res2.text)
    return json_ya['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split(' ')

if __name__ == '__main__':
    r = req('https://www.prachka.com/adresa_prachechnyh.html')
    count = 1
    h = bs4.BeautifulSoup(r.text, 'lxml')
    cities = {o['value']: o.text for o in h.find(attrs=dict(name="city")).find_all('option')}
    for c, city in cities.items():
        city_url = 'https://{}.prachka.com/'.format(c)
        r = req(city_url + 'adresa_prachechnyh.html')

        points = re.findall('createPlacemark\(new YMaps\.GeoPoint\((.+?)\)\);', r.text)
        h = bs4.BeautifulSoup(r.text, 'lxml')

        phone = h.select_one('#bottom strong').get_text(strip=True)
        phone = normalize_phone(phone)
        try:
            adresa = [a.text for a in h.select('#adresa li')]
        except:
            adresa = []

        addresses = []
        if points != []:
            for point in points:
                point = point.replace(u'Омск, бульвар Архитекторов, д.35 (ТЦ МЕГА)<BR>Часы работы: ежедневно с 9.00 до 22.00', u'Омск\', \'бульвар Архитекторов, д.35 (ТЦ МЕГА)<BR>Часы работы: ежедневно с 9.00 до 22.00')
                coords, name, info, foo = re.split(',\s[\'{]', point, maxsplit=4)

                address = re.search('>?([^>]+?)<', info, flags=re.U)
                if address:
                    address = address.group(1)
                else:
                    address = name.strip("'")
                address = address.strip().strip('.')

                ph = ''
                for a in adresa:
                    try:
                        a, phs = a.split(u'Тел')
                    except:
                        continue
                    a = a.split()[-1].strip().strip('.')
                    if re.search(u'{}($|,)'.format(a), address):
                        #phs = phs.split(';')
                        ph = normalize_phone(phs)

                lon, lat = coords.strip().replace(')', '').split(',')
                lat = lat.strip()
                lon = lon.strip()

                wh = re.search(u'работы:?\s?(.+?)(<|\'|$)', info, flags=re.U | re.I)
                if wh:
                    wh = wh.group(1)

                url = re.search('href="(.+?)"', name + info)
                if url:
                    url = city_url + url.group(1)

                if city not in address:
                    address = u'{}, {}'.format(city, address)
                addresses.append(address)
                count += 1
                addXML(count, None, address, ph, lat, lon, wh, url)
        else:
            data = fromstring(r.text)
            city = data.xpath('//select[@name="city"]/option[@selected="selected"]/text()')[0]
            for url in data.xpath('//div[@class="adres"]/strong/a/@href'):
                res = fromstring(requests.get(city_url + '/' + url).text)
                address = city + ', ' + res.xpath('//h2/text()')[0].replace(u'Прачечная по адресу: ', u'').replace(u', прикассовая зона Ашан.', u'')
                address = address.replace(u'От метро пл.Мужества налево, далее в арку за магазином КЕЙ, через 20 метров справа вход в прачечную в подвальное помещение.', u'')
                address = address.replace(u' Здание общежития, №14, вход с торца здания (м. пл. Мужества)', u'')
                address = address.replace(u' (угол с Разъезжей, 27 и Боровой, 2), цокольный этаж торгового центра', u'')
                #address = address.replace(u'', u'')
                address = re.sub(u'\(.*\)', u'', address)

                address = address.replace(u', студ.городок МИЭТ', u'')
                address = address.replace(u', ТЦ "Андреевский Двор" ', u'')
                address = address.replace(u', первый этаж', u'')
                address = address.replace(u' . Метро Проспект Просвещения', u'')
                address = address.replace(u'. Метро Автово', u'')
                address = address.replace(u'. Метро Ленинский проспект', u'')
                address = address.replace(u'"МЕГА Дыбенко", Ашан. ', u'')
                address = address.replace(u' . Метро Чкаловская', u'')
                address = address.replace(u'. Метро Купчино', u'')
                address = address.replace(u'. Метро "Лиговский проспект"', u'')
                address = address.replace(u'МО, ', u'')

                
                wh = res.xpath('//h3/text()')[0].replace(u'График работы прачечной:', u'')
                if wh == [] or wh == u'Как добраться:' or wh == u'Интерьер прачечной:':
                    wh = res.xpath('//td[@colspan="2"]/div/text()')[0].replace(u'Работаем ', u'')
                if wh == u'Телефон: +7 (915) 443-29-33':
                    wh = res.xpath('//h1/text()')[1].replace(u'График работы прачечной:', u'')
                
                phone1 = res.xpath('//h3/text()')[1].replace(u'Телефон: ', u'')
                if phone1 == u'Как добраться:' or phone1 == u'Интерьер прачечной:':
                    phone1 = ''
                count += 1
                
                if address == u'Москва, Одинцово, Можайское шоссе, 122.  ':
                    phone1 = phone
                    wh = u'ежедневно с 09-00 до 21-00'
                addXML(count, None, address, phone1, getLanLon(address)[1], getLanLon(address)[0], wh, city_url + '/' + url)



    x = etree.tounicode(xml, pretty_print=True)
    print("<?xml version='1.0' encoding='utf-8'?>")
    print(x.encode('utf-8'))
