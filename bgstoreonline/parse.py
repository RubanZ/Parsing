# coding=utf-8
import ast
import json
import re
import sys
from time import sleep, time

import requests
from bs4 import BeautifulSoup

requests.urllib3.disable_warnings()


def request(url, decode='utf-8', method='GET', headers={}, data=None, params=None):
    headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:44.0) Gecko/20100101 Firefox/44.0'})
    tries = 0
    while tries < 10:
        try:
            response = requests.request(method, url, headers=headers, timeout=60, data=data, params=params,
                                        verify=False)
            response.encoding = decode
            return response
        except Exception as e:
            sys.stderr.write('try {}\n'.format(tries))
            sys.stderr.write(u'{}\n'.format(e))
            tries += 1
            sleep(5)
    raise Exception('Ошибка соединения')


mainName = u'B&G Store'
mainUrl = u'https://www.bgstoreonline.com'
rubrics = ['184107248']
langv = u'tr'
cantry = u'Türkiye'
addUrls = [u'https://www.facebook.com/bgstoreonline/', u'https://www.instagram.com/bgstoreonline/']


def make_small_from_big(words):
    newWords = u''
    wordsList = words.split()
    for wl in wordsList:
        new_word = wl.lower()
        newWords += u' {}'.format(wl[0] + new_word[1:])
    return newWords.strip()


def bs(html):
    return BeautifulSoup(html, 'html.parser')


def tel_normalize(t):
    if t[0] == u'0':
        t = t[1:]
    return u'+90{} {} {} {} {}'.format(t[:-10], t[-10:-7], t[-7:-4], t[-4:-2], t[-2:])

addresses = []

def custom_coding(str):
    list_changes = [
        ['\u0130', u'İ'],
        ['\u00fc', u'ü'],
        ['\u00d6', u'Ö'],
        ['\u00e7', u'ç'],
        ['\u0131', u'ı'],
        ['\u015f', u'ş'],
        ['\u00f6', u'ö'],
        ['\u00c7', u'Ç'],
        ['\u011f', u'ğ'],
        ['\u015e', u'Ş'],
        ['\u00dc', u'Ü']
    ]
    for ch in list_changes:
        str = re.sub(ch[0], ch[1], str)

    return str

def mainParse():

    r = request('https://www.bgstoreonline.com/storepickup/').text
    json_text = re.search('(\[{"store_id":[\s\S]*?}]);<\/script>', r).group(1)
    json_list = ast.literal_eval(json_text)

    for jsl in json_list:
        jsl = unicode(jsl).replace("'",'"')
        jsl = jsl.replace(u"\"S ", u"'S ")
        store = json.loads(jsl)
        lat, lon = u'', u''
        email = u''
        nameOther = u''
        address = u''
        new_phone, faxes = u'', []

        lat, lon = store['store_latitude'], store['store_longitude']
        nameOther = mainName+' '+make_small_from_big(re.sub(r'\\', u'', re.sub(u'/', u'\/', custom_coding(store['store_name']))).strip())
        city = make_small_from_big(re.sub(r'\\', u'', re.sub(u'/', u'\/', custom_coding(store['city']))).strip())
        addr = make_small_from_big(re.sub(r'\\', u'', re.sub(u'/', u'\/', custom_coding(store['address']))).strip())
        if city not in addr:
            addr = u'{}, {}'.format(addr, city)
        address = re.sub(u' \/ ', u', ', re.sub(u'(\D) ?\/ ?([a-zA-Z]{2,24})', u'\\1, \\2', addr))

        town_from_bs=[
            [u'istanbul', u'İstanbul'],
            [u'ankara', u'Ankara'],
            [u'nevşehir', u'Nevşehir']
        ]

        for tfb in town_from_bs:
            address = re.sub(tfb[0], tfb[1], address)

        town_via_district = [
            [u'Balçova', u'İzmir'],
            [u'Acibadem-üsküdar', u'İstanbul'],
            [u'Esenyurt', u'İstanbul'],
            [u'Beşiktaş', u'İstanbul'],
            [u'Cankaya', u'Ankara'],
            [u'Yenimahalle', u'Ankara'],
            [u'Bakırköy', u'İstanbul'],
            [u'Bayrampaşa', u'İstanbul'],
            [u'Ümraniye', u'İstanbul'],
            [u'Emek', u'İstanbul'],
            [u'Şişli', u'İstanbul'],
            [u'Merkez', u'Ankara'],
            [u'Florya', u'İstanbul'],
            [u'Eyüp', u'İstanbul'],
            [u'Bahçelievler', u'İstanbul'],
            [u'İstinye', u'İstanbul'],
            [u'Alsancak', u'İzmir'],
            [u'Melikgazi', u'Kayseri'],
            [u'Çankaya', u'Ankara'],
            [u'Bornova', u'İzmir'],
            [u'Selçuklu', u'Konya'],
            [u'Başakşehir', u'İstanbul'],
            [u'Karşıyaka', u'İzmir'],
            [u'Kadiköy', u'İstanbul'],
            [u'Canik', u'Samsun'],
            [u'Suadiye', u'Istanbul'],
            [u'Degirmendere', u'Trabzon'],
            [u'Atakum', u'Samsun'],
            [u'Seyhan', u'Adana'],
            [u'Muratpaşa', u'Antalya'],
            [u'Yenişehir', u'Mersin'],
            [u'Nilüfer', u'Bursa'],
            [u'Gaziosmanpaşa', u'İstanbul'],
            [u'Konak', u'İzmir'],
            [u'Beyoğlu', u'İstanbul'],
            [u'Yakutiye', u'Erzurum'],
            [u'Üsküdar', u'İstanbul'],
            [u'Maltepe', u'İstanbul'],
            [u'Kepez', u'Antalya'],
            [u'Battalgazi', u'Malatya'],
            [u'Kartal', u'İstanbul'],
            [u'Altıeylül', u'Balikesir']
        ]

        if u'Çeşme' in address:
            address = re.sub(u'Çeşme', u'', address).strip()+u', Çeşme'

        for tvd in town_via_district:
            if tvd[0] in address:
                address += u', {}'.format(tvd[1])

        address = re.sub(u'No:3/128-129, Altıeylül, İstanbul, Balikesir', u'No:3/128-129, Altıeylül, İstanbul', address)
        address = re.sub(u'İstanbul, İstanbul', u'İstanbul', address)
        address = re.sub(u'Caddesi No:144/z53 Battalgazi, Malatya, Malatya', u'Caddesi No:144/z53 Battalgazi, Malatya', address)
        address = re.sub(u'Antalya, Antalya', u'Antalya', address)
        address = re.sub(u'İzmir, İzmir', u'İzmir', address)
        address = re.sub(u'Istanbul, Istanbul', u'İstanbul', address)
        address = re.sub(u'Blok 33, Bayrampaşa, İstanbul, Ankara', u'Blok 33, Bayrampaşa, İstanbul', address)
        address = re.sub(u'Ankara, İstanbul', u'Ankara', address)
        email = store['store_email']

        phone = store['store_phone']
        if len(phone)> 5:
            new_phone = tel_normalize(re.sub(u'\D', u'', phone))

        jsAddr = {"#content": address, "@lang": langv}
        jsName = {"#content": mainName, "@lang": langv}
        jsNameOth = {"#content": nameOther, "@lang": langv}
        jsCountry = {"#content": cantry, "@lang": langv}
        addresses.append(address)

        jsTels = []
        jsTels.append({"number": new_phone, "type": u"phone", "add_number": "", "info": ""})

        out = {
            "url": mainUrl,
            "add-urls": addUrls,
            "company-id": unicode(addresses.count(address)),
            "rubric_id": rubrics,
            "name": jsName,
            "name_other": jsNameOth,
            "country": jsCountry,
            "address": jsAddr,
            "phone": jsTels,
            "lat": lat,
            "lon": lon,
            "actualization-date": str(int(time()))

        }
        if email:
            out.update({"email": email})
        print(json.dumps(out, ensure_ascii=False).encode('utf-8'))


if __name__ == '__main__':
    mainParse()
