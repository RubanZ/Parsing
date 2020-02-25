# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from multiprocessing.pool import ThreadPool

from lxml import etree
from time import sleep, time
import json
from bs4 import BeautifulSoup
import requests
import sys
import traceback
import re
import difflib


main_country = u'Россия'
lang = 'ru'
main_host = "http://www.orbank.ru/"
main_names = [u'Банк Оренбург', u'Банк Оренбург, банкомат', u'Банк Оренбург, платёжный терминал']
rubricss = [["184105398"], ["184105402"], ["184106974"]]
main_phones = ["+7 (353) 234 31 03"]

xml = etree.Element('companies')


def normalizePhone(phone):
    phone = phone.strip()
    if not phone or phone == '-':
        return None

    phone = re.sub('\D', '', phone)
    phone = re.sub('^0', '', phone)
    phone = re.sub('^90', '', phone)

    country_code = '+7'
    code, number = phone[:3], phone[3:]
    number = number[:3] + ' ' + number[3:5] + ' ' + number[-2:]
    phone = country_code + ' (' + code + ') ' + number

    return phone



def req(url, decode='utf-8', method='GET', headers={}, data=None, params=None):
    tries = 0
    while tries < 10:
        try:
            response = requests.request(method, url, headers=headers, timeout=60, data=data, params=params,
                                        verify=False)
            if response.status_code != 200:
                raise Exception('Status code is not OK')
            response.encoding = decode
            return response
        except Exception as e:
            sys.stderr.write('try {}\n'.format(tries))
            sys.stderr.write(u'{}\n'.format(e))
            tries += 1
            sleep(5)
    raise Exception('Ошибка соединения')


def add_xml(company_id, name_other, add_urls, addr, wh, phones, faxes, emails, lat, lon):
    main_name = main_names[feednum-1]
    rubrics = rubricss[feednum-1]

    company = etree.Element('company')
    etree.SubElement(company, 'company-id').text = str(company_id)

    for rubric in rubrics:
        etree.SubElement(company, 'rubric-id').text = rubric

    etree.SubElement(company, 'url').text = main_host

    name = etree.SubElement(company, 'name')
    name.text = main_name
    name.set('lang', lang)

    if name_other:
        nameother = etree.SubElement(company, 'name-other')
        nameother.text = name_other
        name.set('lang', lang)

    for a in add_urls:
        etree.SubElement(company, 'add-url').text = a

    country = etree.SubElement(company, 'country')
    country.text = main_country
    country.set('lang', lang)

    address = etree.SubElement(company, 'address')
    address.text = addr
    address.set('lang', lang)

    # if add_addr:
    #     address_add = etree.SubElement(company, 'address-add')
    #     address_add.text = add_addr
    #     address_add.set('lang', lang)

    for mph in main_phones:
        phone = etree.SubElement(company, 'phone')
        etree.SubElement(phone, 'ext')
        etree.SubElement(phone, 'type').text = 'phone'
        etree.SubElement(phone, 'number').text = mph
        etree.SubElement(phone, 'info')

    for ph in phones:
        if ph:
            s = re.search('\s?\((\D+?)\)', ph)
            ph = re.sub('\s?\((\D+?)\)', '', ph)
            phone = etree.SubElement(company, 'phone')
            etree.SubElement(phone, 'ext')
            etree.SubElement(phone, 'type').text = 'phone'
            p = normalizePhone(re.sub('[^\d() \-+]', '', ph))
            p = p.replace(u'+7 (3532) 343-103', u'+7 (353) 234 31 03')
            etree.SubElement(phone, 'number').text = p
            if s:
                etree.SubElement(phone, 'info').text = s.group(1)
            else:
                etree.SubElement(phone, 'info')
    for f in faxes:
        if f:
            phone = etree.SubElement(company, 'phone')
            etree.SubElement(phone, 'ext')
            etree.SubElement(phone, 'type').text = 'fax'
            etree.SubElement(phone, 'number').text = f
            etree.SubElement(phone, 'info')

    for email in emails:
        if email:
            etree.SubElement(company, 'email').text = email

    if wh:
        working_time = etree.SubElement(company, 'working-time')
        working_time.text = wh
        working_time.set('lang', lang)

    if lat and lon:
        coordinates = etree.SubElement(company, 'coordinates')
        lt = etree.SubElement(coordinates, 'lat')
        lt.text = str(lat)
        ln = etree.SubElement(coordinates, 'lon')
        ln.text = str(lon)

    etree.SubElement(company, 'actualization-date').text = str(int(time()))
    xml.append(company)


def parse_wh_orenburg(tr):
    ps = tr.select("p")
    start_i = -1
    finish_i = -1
    for i in range(0, len(ps)):
        p = ps[i]
        if u"p_cb" in p["class"]:
            if start_i != -1:
                finish_i = i
            elif u"физических" in p.text.lower():
                start_i = i
    if start_i == -1:
        return None
    if finish_i == -1:
        finish_i = len(ps)
    wh_array = []
    for i in range(start_i+1, finish_i):
        p = ps[i]
        if u"вых" not in p.text.lower():
            wh_array.append(p.text.strip())
    wh = "; ".join(wh_array)
    return wh


def parse_orenburg():
    soup = BeautifulSoup(req("http://www.orbank.ru/about/contacts.php").text, "html.parser")
    offices = {}
    tables = soup.select("div.content-block.news-list table")

    head_office = tables[0].select("tr")
    head_addr = u"г. Оренбург, " + head_office[1].text.strip()
    head_phones = [head_office[2].select("td")[1].text.strip()]
    head_faxes = [head_office[3].select("td")[1].text.strip()]
    head_emails = [head_office[4].select("td")[1].text.strip()]
    head_wh = parse_wh_orenburg(head_office[5])
    offices[head_addr] = {"phones": head_phones, "faxes": head_faxes, "emails": head_emails, "wh": head_wh}

    other_offices = zip(*[iter(tables[1].select("tr"))]*3)
    for office in other_offices:
        office_addr = u"г. Оренбург, " + office[0].text.strip()

        office_phones = []
        phones_unsplitted = office[1].select("td")[1]
        strings = [x.strip() for x in phones_unsplitted.text.split("\n") if x.strip() != u""]
        for string in strings:
            office_phones.append(string)

        office_wh = parse_wh_orenburg(office[2])

        offices[office_addr] = {"phones": office_phones, "faxes": [], "emails": [], "wh": office_wh}

    return offices


def parse_data():
    if feednum == 1:
        orenburg_data = parse_orenburg()
    parse_url = "http://www.orbank.ru/region/address.js"
    js_data = req(parse_url).text
    js_data = re.sub(u"\/\/.*,'.*'],", u'', js_data)
    js_data = js_data.replace(u'\n', u'').replace(u'\r', u'')
    
    if feednum == 1:
        regex = r"var\s+address_o\s+=\s+(\[(?:(?!\];).)+\]);"
    elif feednum == 2:
        regex = r"var\s+address_b\s+=\s+(\[(?:(?!\];).)+\]);"
    else:
        regex = r"var\s+address_k\s+=\s+(\[(?:(?!\];).)+\]);"
        
    result = re.findall(regex, js_data)[0]
    result.strip()
    if result[-1] == ";":
        result = result[:-1]
    result = result.replace("\"", "%temp%")
    result = result.replace("\'", "\"")
    result = result.replace("%temp%", "\'")
    
    
    json_data = json.loads(result.encode('utf-8'))
    for item in json_data:
        lat = str(item[0])
        lon = str(item[1])
        addr = ''
        addresses = re.search(u'.* (\S. .*,.*, .*)', item[2])
        if addresses is not None:
            addr = addresses.group(1)
        if addr == u"1-й Домбаровский пер., дом 41":
            addr = u"г. Орск, " + addr
        addr = addr.replace(u'с. Александровка с.Александровка, ул. Мичурина, 22', u'с.Александровка, ул. Мичурина, 22')
        addr = addr.replace(u'40 лет Октября, дом 16, В Отделение Банка', u'с. Северное, 40 Лет Октября ул., 16А')
        if addr == '' and lat == '51.4787024055':
            addr = u'г. Кувандык, Оренбургская ул., 20'
        if addr == '' and lat == '52.4099160122':
            addr = u'г. Сорочинск, ул. Фурманова, 105'
        if addr == '' and lat == '51.7889919758':
            addr = u'г. Оренбург, ул. Расковой, 10А'
        if addr == '' and lat == '51.7749052488':
            addr = u'г. Оренбург, пр. Гагарина, 54/1'
        if addr == '' and lat == '51.7739930006':
            addr = u'г. Оренбург, пр. Гагарина, 11'
        if addr == '' and lat == '51.4771937437':
            addr = u'г. Кувандык, ул. Ленина, 114'
        if addr == '' and lat == '51.46166062':
            continue
        if addr == '' and lat == '51.4615404412':
            continue
        if addr == '' and lat == '51.4669467456':
            addr = u'г. Гай, ул. Ленина, 27'
        if addr == '' and lat == '51.4642759418':
            addr = u'г. Гай, Октябрьская ул., 113'
        if addr == '' and lat == '51.7686817484':
            addr = u'г. Оренбург, ул. Володарского, 39'
        if addr == '' and lat == '51.7891340952':
            addr = u'г. Оренбург, ул. Марины Расковой, 10А'
        if addr == '' and lat == '52.3405883313':
            addr = u'п. Тюльган, ул. Ленина, 10/27'
        if addr == '' and lat == '51.3981105834':
            addr = u'г. Медногорс, ул. Гагарина, 6'
        wh = None
        phones = []
        faxes = []
        emails = []
        add_urls = []
        name_other = None
        if feednum == 1:
            if len(item) == 6:
                add_urls = ["http://www.orbank.ru/region/"+item[5]]
                soup = BeautifulSoup(req(add_urls[0]).text, "html.parser")
                name_other = soup.select("div.content-block h2")[0].text

                table_left_tr = soup.select("table.leftthis")[0].select("tr")

                i = -1
                for tr_id in range(0, len(table_left_tr)):
                    tr = table_left_tr[tr_id]
                    if u"физических" in tr.text:
                        i = tr_id
                        break
                if i != -1:
                    wh_tds = table_left_tr[i+1:]
                    wh_text = [td.text.strip() for td in wh_tds if u"Вых" not in td.text]
                    wh = re.sub("\s+", " ", "; ".join(wh_text))

                phone_tr = None
                for tr in table_left_tr:
                    tds = tr.select("td")
                    if len(tds) >= 2:
                        if u"телефон" in tds[0].text.lower():
                            phone_tr = tr
                            break
                if phone_tr:
                    phones_unsplitted = phone_tr.select("td")[1]
                    strings = [x.strip() for x in phones_unsplitted.text.split("\n") if x.strip()!=u""]
                    for string in strings:
                        if u"(факс)" in string.lower():
                            faxes.append(string.replace(u"(факс)", u"").strip())
                        else:
                            phones.append(string)
            else:
                add_urls.append("http://www.orbank.ru/about/contacts.php")
                known_addrs = orenburg_data.keys()
                city_data = None

                ratios = [difflib.SequenceMatcher(a=addr.replace(u"г. Оренбург, ", u""), b=known_addr).ratio() for known_addr in known_addrs]
                best_id = ratios.index(max(ratios))
                datas = orenburg_data[known_addrs[best_id]]

                wh = datas["wh"]
                phones = datas["phones"]
                faxes = datas["faxes"]
                emails = datas["emails"]

        if not wh:
            wh = item[4].split("<br>")
            for day in wh:
                if u"вых" in day:
                    wh.remove(day)
            wh = [s.strip() for s in wh]
            wh = "; ".join(wh).strip()

        add_xml(1, name_other, add_urls, addr, wh, phones, faxes, emails, lat, lon)


def read_arguments_feednumber():
    argp = ArgumentParser()
    argp.add_argument('--feed', type=int, default=3)
    args = argp.parse_args()
    return args.feed


if __name__ == "__main__":
    try:
        feednum = read_arguments_feednumber()
        parse_data()
        x = etree.tounicode(xml, pretty_print=True)
        print("<?xml version='1.0' encoding='utf-8'?>")
        print(x.encode('utf-8'))
    except:
        sys.stderr.write(traceback.format_exc().encode('utf-8'))
        sys.stderr.flush()
