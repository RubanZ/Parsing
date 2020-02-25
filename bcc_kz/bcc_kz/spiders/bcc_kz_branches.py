# -*- coding: utf-8 -*-
import json
import re
import sys
from HTMLParser import HTMLParser
from time import time

import scrapy

item_type = 'F'

main_country = u'Казахстан'
lang = 'ru'
main_host = 'https://www.bcc.kz'
main_name = u'Банк ЦентрКредит'

rubrics = ['184105398']

add_urls = u''''''.split('\n')
main_phones = []


def prep_dictionary(id, o_name, addr, phones, lat, lon, wh=u'', emails='', addr_add='', url=''):
    out = {'company-id': str(id), 'rubric_id': rubrics, 'add_url': []}

    for a in add_urls:
        if a:
            out['add_url'].append(a)

    if url:
        out['add_url'].append(url)

    out['url'] = main_host

    out['name'] = {'#content': main_name, '@lang': 'ru'}

    if o_name:
        out['name_other'] = {'#content': o_name, '@lang': lang}

    out['address'] = {'#content': addr, '@lang': lang}

    if addr_add:
        out['address_add'] = {'#content': addr_add, '@lang': lang}

    out['country'] = {'#content': main_country, '@lang': lang}

    out['phone'] = []

    for p in main_phones:
        out['phone'].append({'number': p, 'add-number': '', 'type': 'phone'})

    for p in phones:  # !
        out['phone'].append({'number': p['p'], 'add-number': p['a'], 'type': p['t'], 'info': p['i']})

    out['email'] = emails

    out['working_time'] = {'#content': wh, '@lang': lang}

    out.update({'lat': lat, 'lon': lon})

    out['actualization_date'] = str(int(time()))

    return out


def normalize_phone(phone, country_code='+7'):  # kz
    if not phone:
        return None

    phone = phone.strip()
    if not phone or phone == '-':
        return None

    phone = re.sub('\D', '', phone)
    phone = re.sub('^8', '', phone)

    phone = phone[:10]

    if len(phone) == 10:
        code, number = phone[:3], phone[3:]
        number = number[:3] + '-' + number[3:5] + '-' + number[-2:]
        phone = country_code + ' (' + code + ') ' + number
        return phone


def normalize_address(addr):
    addr = addr.strip()
    addr = re.sub('^\d{5,6},?\s?', '', addr)
    addr = re.sub('[()]', '', addr)
    addr = re.sub('["\']', '', addr)
    addr = addr.replace('&nbsp;', ' ')
    addr = re.sub(r'([.,])(\w)', r'\1 \2', addr, flags=re.U)
    addr = re.sub('\s+', ' ', addr)

    addr = addr.replace(u' ', ' ')
    return addr


class BccKzBranchesSpider(scrapy.Spider):
    name = 'bcc_kz_branches'
    allowed_domains = ['bcc.kz']
    start_urls = ['https://www.bcc.kz/branches-and-atms/']
    html_parser = HTMLParser()

    def parse(self, response):
        options = response.xpath('//option[@type="{}"]'.format(item_type))

        for o in options:
            city = o.xpath('text()').get()
            value = o.xpath('@value').get()
            if 'pydevd' in sys.modules and city != u'Алматы':
                continue
            yield scrapy.Request(
                'https://www.bcc.kz/local/tmpl/ajax/getmap.php?type={}&city={}&lang=s1'.format(item_type, value),
                self.get_map, meta=dict(value=value, city=city))

    def get_map(self, response):
        value = response.meta['value']
        city = response.meta['city']

        text = response.text
        text = re.sub(r'\\\n', '', text)
        data = json.loads(text)

        items = []

        if 'markers' in data:
            for d in data['markers']:
                address = d['address']
                address = address.replace('&nbsp;', ' ')

                # for the shit like this:
                # u'&lt;p&gt;\r\nул.Торайгырова, 53/23\r\n&lt;/p&gt;'
                address = self.html_parser.unescape(address)
                address = scrapy.Selector(text=address).xpath('//text()').get("").strip()
                address = address.replace(u'\xa0', ' ')

                name = d['name']
                name = name.replace(u'\xa0', ' ')


                items.append(dict(
                    name=name.strip(),
                    address=address.strip(),
                    lat=d['lat'],
                    lon=d['lng'],
                ))

        return response.follow(
            'https://www.bcc.kz/local/tmpl/ajax/getmapdata.php?type={}&city={}&lang=s1'.format(item_type, value),
            self.get_map_data, meta=dict(items=items, city=city))

    def get_map_data(self, response):
        items = response.meta['items']
        city = response.meta['city']

        data = response.css('.aa_mt_body')

        out_items = []

        for d in data:
            body_items = d.css('.aa_mt_bodyitem')
            name = body_items[0].xpath('.//text()').get('').strip()

            comm = body_items[2].xpath('.//text()').getall()

            phones = []
            email = ''

            last_phone = None
            for c in comm:
                c = c.strip()
                c = c.replace(u'\xa0', ' ')
                if not c or 'SWIFT' in c:
                    continue
                if '@' in c or 'mail' in c:
                    email = c.split(':')[-1].strip()
                else:
                    c_split = re.split(ur'\s[-–]\s', c)
                    info = ''
                    if len(c_split) == 2:
                        info = c_split[-1]

                    p = c_split[0].strip()
                    if not re.search('\d', p):
                        tmp = p
                        p = info
                        info = tmp

                    add_numbers = []
                    s = re.search(u'вн[:. ;](.+)', p, flags=re.I | re.U)
                    if s:
                        p = p.replace(s.group(0), '').strip()

                        add_numbers = s.group(1)
                        add_numbers = re.findall('([\d ]+)', add_numbers)
                        add_numbers = [x for x in (re.sub('\D', '', a) for a in add_numbers) if x]

                    if not p and last_phone:
                        p = last_phone
                    last_phone = p

                    last_ph = None
                    p_split = p.split(',')
                    for ph in p_split:
                        ph = re.sub(u'\D', u'', ph)
                        if ph:
                            if last_ph and len(ph) < 10:
                                ph = last_ph[:-len(ph)] + ph
                            last_ph = ph
                            ph = normalize_phone(ph)
                            if ph:
                                t = 'phone'
                                if re.search(ur'^факс', info, flags=re.I | re.U):
                                    info = ''
                                    t = 'fax'
                                if re.search(ur'^тел\.?/факс', info, flags=re.I | re.U):
                                    info = ''
                                    t = 'phone-fax'

                                phone = dict(p=ph, a='', i=info, t=t)
                                if add_numbers:
                                    for a in add_numbers:
                                        tmp = dict(phone, a=a)
                                        if tmp not in phones:
                                            phones.append(tmp)
                                else:
                                    phones.append(phone)



            wh = body_items[3].xpath('.//text()').getall()
            wh = ' '.join(wh).strip()
            wh = re.sub('\s+', ' ', wh)
            wh = re.search(u'Физические лица:?(.+?)', wh, flags=re.I | re.U) #Физ.+?лиц.?:?(.+?)($|бизнес)
            if wh:
                wh = wh.group(1)
            else:
                wh = ''

            address = body_items[1].xpath('.//text()').get('').strip()
            address = address.replace(u'\xa0', ' ')

            item = {'lat': '', 'lon': ''}
            for i in items:
                if i['name'] == name and i['address'] == address:
                    items.remove(i)
                    item = i
                    break

            # if not item:
            #     logging.error(u'Match not found in city {} for: {}'.format(city, address))

            address = normalize_address(address)
            if not re.search(u'(^| )[гпс]\.', address):
                address = u'{}, {}'.format(city, address)
            out = prep_dictionary(None, name, address, phones, item['lat'], item['lon'], wh, email)

            # Не приносим первый филиал города без времени работы, если он дублирует второй.
            # Пример: https://yadi.sk/i/KtOESFOOfbpH9w
            if out_items:
                last = out_items[-1]
                if last['address']['#content'] == out['address']['#content'] and not last['working_time']['#content']:
                    out_items.remove(last)

            out_items.append(out)

        return out_items
