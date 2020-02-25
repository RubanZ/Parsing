# coding=utf-8
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

def make_small_from_big(words):
    newWords=u''
    wordsList=words.split()
    for wl in wordsList:
        new_word=wl.lower()
        newWords+=u' {}'.format(wl[0]+new_word[1:])
    return newWords.strip()

def bs(html):
    return BeautifulSoup(html, 'html.parser')

mainUrl=u'https://www.macfit.com.tr/'
mainName = u'MACFit'
langv = u'tr'
cantry = u'Türkiye'
addUrls = [
    u'https://twitter.com/macfitofficial',
    u'https://www.instagram.com/macfitofficial/',
    u'https://www.facebook.com/MACFitOfficial'
]
rubrics = ['184107363', '41430094175']

def tel_normalize(t):
    #+90 312 123 45 67
    return u'{} {} {} {} {}'.format(t[:-10], t[-10:-7], t[-7:-4], t[-4:-2], t[-2:])

def main_parse(url):
    firstData = []
    res = request(url).text
    soup = bs(res)
    ul = soup.find('ul', {'class':u'step-content-2'})
    lies = ul.find_all('li')
    for l in lies:
        a = l.find('a')
        if a:
            href = mainUrl+a.get('href')[1:]
            name = a.text.strip()
            firstData.append([href, name])
    for d in firstData:
        wTime, address = u'', u''
        lat, lon = u'', u''
        item_url = d[0]
        # print item_url
        add_urls = addUrls+[item_url]
        nameOther = make_small_from_big(d[1])
        # print nameOther
        #print(request(item_url).text)
        newSoup = bs(request(item_url).text)

        time_span = newSoup.find('span', {'class':u'm-t-5'})
        all_time = re.sub(u'(\d{1,2}:\d{1,2})([\s\S]*?)(\d{1,2}:\d{1,2})', u'\\1-\\3',  unicode(time_span)).split('<br/>')
        all_time[1] = all_time[1].replace(u'8.00', '8:00')
        f_time = u'Pazartesi-Cuma: {}'.format(re.findall('\d{1,2}:\d{1,2}-\d{1,2}:\d{1,2}', all_time[0])[0])
        s_time = u'Cumartesi-Pazar: {}'.format(re.findall('\d{1,2}:\d{1,2}-\d{1,2}:\d{1,2}', all_time[1])[0])
        wTime = u'{}, {}'.format(f_time, s_time)
        # print wTime

        search_href = newSoup.select('section[id=mapSection] > iframe')
        if search_href:
            coords_url = search_href[0].get('src')
            allCoords = re.search('!2d(.*)!3d(.*)!3m2!(.*)!3m3!', coords_url)
            #print coords_url
            #print(allCoords.group(2))
            lat, lon = allCoords.group(2), allCoords.group(1)
            # print u'{}, {}'.format(lat, lon)

        addr = newSoup.select('div[class=text-wrap-right] > div[class=text-row] > div[class=text-inner] > span[class=text]')[0]
        address = make_small_from_big(re.sub(u' ?- ?', u', ', re.sub(u' ?\/ ?', u', ', addr.text.strip())))
        address = re.sub(u' {2,255}', u'', re.sub(u'\([\s\S]*?\)', '', re.sub('\d{4,255}', u'', address)))

        photos = []

        gallery_div = newSoup.select('div[class=gallery-wrapper-inner] > div > ul[class=swiper-wrapper]')
        if gallery_div:
            all_links = gallery_div[0].find_all('a')
            for a in all_links:
                image_url = mainUrl+a.get('href')[1:]
                if 'avascript' not in image_url:
                    photos.append(image_url)



        if len(address)>2:
            jsAddr = {"#content": address, "@lang": langv}
            jsName = {"#content": mainName, "@lang": langv}
            jsNameOther = {"#content": nameOther, "@lang": langv}
            jsCountry = {"#content": cantry, "@lang": langv}
            addresses.append(address)
            out = {
                "url": mainUrl,
                "add-urls": add_urls,
                "company-id": str(addresses.count(address)),
                "rubric_id": rubrics,
                "name": jsName,
                "name_other": jsNameOther,
                "country": jsCountry,
                "address": jsAddr,
                # "lat": lat,
                # "lon": lon,
                "actualization-date": str(int(time()))
            }
            if lat and lon:
                out.update({"lat": lat, "lon": lon})
                # print u'{}, {}'.format(lat, lon)
            if len(photos)>0:
                out.update({"photo": photos})
            print(json.dumps(out, ensure_ascii=False).encode('utf-8'))

addresses=[]

if __name__ == '__main__':
    main_parse('https://www.macfit.com.tr/')
