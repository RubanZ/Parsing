# coding=utf-8
import json
import re
import sys
from argparse import ArgumentParser
from time import sleep
from time import time

import requests
from bs4 import BeautifulSoup

requests.urllib3.disable_warnings()

def request(url, decode='utf-8', method='POST', headers={}, data=None, params=None):
    headers.update({'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'})
    tries = 0
    while tries < 100:
        try:
            response = requests.request(method, url, headers=headers, timeout=80, data=data, params=params,
                                        verify=False)
            if response.status_code != 200:
                raise Exception('Status code {} {}'.format(response.status_code, url))

            return response

        except Exception as e:
            sys.stderr.write('try {}\n'.format(tries))
            sys.stderr.write(u'{}\n'.format(e))
            tries += 1
            sleep(1)
    raise Exception('Ошибка соединения')


def read_arguments():
    argp = ArgumentParser()
    argp.add_argument('--threads', type=int, default=1)
    args = argp.parse_args()
    return args.threads


def gettingViaComp(patt, myText):
    comp = re.compile(patt)
    return comp.findall(myText)[0]


def telNormolize(tel):
    if tel == u'+7(495) 926 34 75':
        return u'+7 (495) 926-34-75'
    else:
        if tel[0] == '8':
            tel = u'+7{}'.format(tel[1:])

        def toFormat(n):
            if len(n) == 12:
                return u'{} ({}) {}-{}-{}'.format(n[:-10], n[-10:-7], n[-7:-4], n[-4:-2], n[-2:])
            else:
                return u'{} ({}) {}-{}-{}'.format(n[:-9], n[-9:-6], n[-6:-4], n[-4:-2], n[-2:])

        number = re.sub('-', '', re.sub('[()]', '', re.sub(' ', '', tel)))
        return toFormat(number)


def make_small_from_big(words):
    newWords = u''
    wordsList = words.split()
    for wl in wordsList:
        new_word = wl.lower()
        newWords += u' {}'.format(wl[0] + new_word[1:])
    return newWords.strip()


def makeTimeWork(str):
    outStr = ''
    locList = str.split('</br>')
    for ll in locList:
        if u'выходн' in ll:
            pass
        else:
            outStr += u' {}'.format(ll)
    return outStr.strip()


mainName = u'Calzedonia'
mainUrl = u'https://ru.calzedonia.com'
rubrics = ['184107963', '184107943', '184107933']
langv = u'en'
cantry = u'Russia'
mainPhone = u'8 (800) 100-07-02'

def reqCity(url, lat, lon, city):
    data = "form_state=locateStoreForm&useCurrentLocation=yes&latitude=" + lon + "&longitude=" + lat + "&storeGroupIdList=&cityStateZipGA=&cityStateZip=&radius=10"
    r = requests.post(url, data=data, headers={
       'content-type': 'application/x-www-form-urlencoded' 
    })
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup.find_all('script', {'type': 'text/javascript'})


def mainParse(url):
    outData = []
    citys = [
        {
            "lat": "40.098548",
            "city": "Maykop",
            "lon": "44.608865"
        },
        {
            "lat": "55.958727",
            "city": "Ufa",
            "lon": "54.735147"
        },
        {
            "lat": "107.584574",
            "city": "Ulan-Ude",
            "lon": "51.834464"
        },
        {
            "lat": "47.504682",
            "city": "Makhachkala",
            "lon": "42.98306"
        },
        {
            "lat": "44.81624",
            "city": "Magas",
            "lon": "43.171501"
        },
        {
            "lat": "43.607072",
            "city": "Nalchik",
            "lon": "43.485259"
        },
        {
            "lat": "44.269759",
            "city": "Elista",
            "lon": "46.307743"
        },
        {
            "lat": "34.346878",
            "city": "Petrozavodsk",
            "lon": "61.785017"
        },
        {
            "lat": "50.836399",
            "city": "Syktyvkar",
            "lon": "61.668793"
        },
        {
            "lat": "34.100318",
            "city": "Simferopol",
            "lon": "44.948237"
        },
        {
            "lat": "47.886089",
            "city": "Yoshkar-Ola",
            "lon": "56.630842"
        },
        {
            "lat": "45.183938",
            "city": "Saransk",
            "lon": "54.187433"
        },
        {
            "lat": "129.732609",
            "city": "Yakutsk",
            "lon": "62.028082"
        },
        {
            "lat": "44.68196",
            "city": "Vladikavkaz",
            "lon": "43.02115"
        },
        {
            "lat": "49.108795",
            "city": "Kazan",
            "lon": "55.796289"
        },
        {
            "lat": "94.437757",
            "city": "Kyzyl",
            "lon": "51.719086"
        },
        {
            "lat": "53.204843",
            "city": "Izhevsk",
            "lon": "56.852593"
        },
        {
            "lat": "91.442387",
            "city": "Abakan",
            "lon": "53.721152"
        },
        {
            "lat": "45.694909",
            "city": "Terrible",
            "lon": "43.317776"
        },
        {
            "lat": "47.251079",
            "city": "Cheboksary",
            "lon": "56.146277"
        },
        {
            "lat": "83.776856",
            "city": "Barnaul",
            "lon": "53.346785"
        },
        {
            "lat": "113.499432",
            "city": "Chita",
            "lon": "52.033973"
        },
        {
            "lat": "158.643566",
            "city": "Petropavlovsk-Kamchatsky",
            "lon": "53.024075"
        },
        {
            "lat": "38.975313",
            "city": "Krasnodar",
            "lon": "45.03547"
        },
        {
            "lat": "92.852572",
            "city": "Krasnoyarsk",
            "lon": "56.010563"
        },
        {
            "lat": "56.229398",
            "city": "Perm",
            "lon": "58.010374"
        },
        {
            "lat": "41.969083",
            "city": "Stavropol",
            "lon": "45.044521"
        },
        {
            "lat": "135.071917",
            "city": "Khabarovsk",
            "lon": "48.480223"
        },
        {
            "lat": "127.527173",
            "city": "Blagoveshchensk",
            "lon": "50.29064"
        },
        {
            "lat": "48.033574",
            "city": "Astrakhan",
            "lon": "46.347869"
        },
        {
            "lat": "36.587223",
            "city": "Belgorod",
            "lon": "50.59566"
        },
        {
            "lat": "34.363407",
            "city": "Bryansk",
            "lon": "53.243562"
        },
        {
            "lat": "40.406635",
            "city": "Vladimir",
            "lon": "56.129057"
        },
        {
            "lat": "44.51693",
            "city": "Volgograd",
            "lon": "48.707073"
        },
        {
            "lat": "39.891523",
            "city": "Vologda",
            "lon": "59.220496"
        },
        {
            "lat": "39.200269",
            "city": "Voronezh",
            "lon": "51.660781"
        },
        {
            "lat": "40.973921",
            "city": "Ivanovo",
            "lon": "57.000348"
        },
        {
            "lat": "104.281047",
            "city": "Irkutsk",
            "lon": "52.287054"
        },
        {
            "lat": "20.507307",
            "city": "Kaliningrad",
            "lon": "54.70739"
        },
        {
            "lat": "36.261215",
            "city": "Kaluga",
            "lon": "54.513845"
        },
        {
            "lat": "86.088374",
            "city": "Kemerovo",
            "lon": "55.354727"
        },
        {
            "lat": "49.668014",
            "city": "Kirov",
            "lon": "58.603591"
        },
        {
            "lat": "40.926858",
            "city": "Kostroma",
            "lon": "57.767961"
        },
        {
            "lat": "65.341118",
            "city": "Kurgan",
            "lon": "55.441004"
        },
        {
            "lat": "36.192647",
            "city": "Kursk",
            "lon": "51.730361"
        },
        {
            "lat": "30.315868",
            "city": "Saint Petersburg",
            "lon": "59.939095"
        },
        {
            "lat": "39.59922",
            "city": "Lipetsk",
            "lon": "52.60882"
        },
        {
            "lat": "150.808541",
            "city": "Magadan",
            "lon": "59.568164"
        },
        {
            "lat": "37.622504",
            "city": "Moscow",
            "lon": "55.753215"
        },
        {
            "lat": "44.005986",
            "city": "Nizhny Novgorod",
            "lon": "56.326887"
        },
        {
            "lat": "31.269915",
            "city": "Veliky Novgorod",
            "lon": "58.52281"
        },
        {
            "lat": "82.92043",
            "city": "Novosibirsk",
            "lon": "55.030199"
        },
        {
            "lat": "73.368212",
            "city": "Omsk",
            "lon": "54.989342"
        },
        {
            "lat": "55.096955",
            "city": "Orenburg",
            "lon": "51.768199"
        },
        {
            "lat": "36.063837",
            "city": "Eagle",
            "lon": "52.970371"
        },
        {
            "lat": "45.018316",
            "city": "Penza",
            "lon": "53.195063"
        },
        {
            "lat": "28.332065",
            "city": "Pskov",
            "lon": "57.81925"
        },
        {
            "lat": "39.720349",
            "city": "Rostov-on-don",
            "lon": "47.222078"
        },
        {
            "lat": "39.736375",
            "city": "Ryazan",
            "lon": "54.629216"
        },
        {
            "lat": "50.101783",
            "city": "Samara",
            "lon": "53.195538"
        },
        {
            "lat": "46.034158",
            "city": "Saratov",
            "lon": "51.533103"
        },
        {
            "lat": "142.738023",
            "city": "Yuzhno-Sakhalinsk",
            "lon": "46.959155"
        },
        {
            "lat": "60.597465",
            "city": "Ekaterinburg",
            "lon": "56.838011"
        },
        {
            "lat": "32.045251",
            "city": "Smolensk",
            "lon": "54.782635"
        },
        {
            "lat": "41.452274",
            "city": "Tambov",
            "lon": "52.721219"
        },
        {
            "lat": "35.911896",
            "city": "Tver",
            "lon": "56.859611"
        },
        {
            "lat": "84.947649",
            "city": "Tomsk",
            "lon": "56.48464"
        },
        {
            "lat": "37.617348",
            "city": "Tula",
            "lon": "54.193122"
        },
        {
            "lat": "65.534328",
            "city": "Tyumen",
            "lon": "57.153033"
        },
        {
            "lat": "48.403123",
            "city": "Ulyanovsk",
            "lon": "54.314192"
        },
        {
            "lat": "61.402554",
            "city": "Chelyabinsk",
            "lon": "55.159897"
        },
        {
            "lat": "39.893787",
            "city": "Yaroslavl",
            "lon": "57.626569"
        },
        {
            "lat": "37.622504",
            "city": "Moscow",
            "lon": "55.753215"
        },
        {
            "lat": "30.315868",
            "city": "Saint Petersburg",
            "lon": "59.939095"
        },
        {
            "lat": "53.006926",
            "city": "Naryan-Mar",
            "lon": "67.63805"
        },
        {
            "lat": "69.018902",
            "city": "Khanty-Mansiysk",
            "lon": "61.00318"
        },
        {
            "lat": "177.508924",
            "city": "Anadyr",
            "lon": "64.733115"
        },
        {
            "lat": "66.614399",
            "city": "Salekhard",
            "lon": "66.529844"
        }
    ]

    for city in citys:

        bigList = reqCity(url, city['lat'], city['lon'], "")#city['city'])
        

        for bl in bigList:
            btext = bl.text
            btext = btext.replace('&apos;', '')
            btext = btext.replace('Tol Yatti', 'Tolyatti')
            btext = btext.replace('Ul Yanovsk', 'Ulyanovsk')
            btext = btext.replace('Moskva', 'Moscow')
            if u'\'RU\'' in btext and u'store.ADDRESS_LINE_1' in btext:
                #print bl
                # print '\n\n'
                tel, timeW = u'', u''
                # print btext

                # compAU = re.compile(r'store.URL = \'([\s\S]*?)\';')
                #addUrl = u'{}{}'.format(mainUrl, re.search(u'store\.URL=\'([\s\S]*?)\';', btext).group(1))
                # print u'\n'+addUrl
                c = re.search(u'store\.COUNTRY_CODE=\'([\s\S]*?)\';', btext).group(1)# store.COUNTRY_CODE='RU';
                # if c != 'RU':
                #     continue
                # compAddr = re.compile(r'store.ADDRESS_LINE_1 = "([\s\S]*?)";')
                SPaddr = re.search(u'store\.ADDRESS_LINE_1 = "([\s\S]*?)";', btext).group(1)
                # print SPaddr

                # compTown = re.compile(r'store.CITY = "([\s\S]*?)";')
                town = re.search(u'store\.CITY = "([\s\S]*?)";', btext).group(1)
                # print town

                addr = re.sub(',(\S)', ', \\1', make_small_from_big(u'{}, {}'.format(town, SPaddr)))
                forDelPatt = [
                    u'Shop A074-075, ',
                    u'Unit 2.49, ',
                    u'Unit A28, ',
                    u'Shop A36, ',
                    u'Shop 167a, ',
                    u'\'\'',
                    u' \(cross\)'
                ]
                for fdp in forDelPatt:
                    addr = re.sub(fdp, u'', addr)
                addr = re.sub(u'Moscow, Moscow,', u'Moscow,', addr)
                addr = re.sub(u'Gor\' Kogo', u'Gor\'kogo', addr)
                # print addr

                compNO = re.compile(r'store\.STORE_NAME = "([\s\S]*?)";')
                nameOth = make_small_from_big(u'{} {}'.format(mainName, compNO.findall(btext)[0]))
                # print nameOth

                compLat = re.compile(r'store\.LATITUDE = \'(\d{1,4}\.\d{1,25})\';')
                lat = compLat.findall(btext)[0]

                compLon = re.compile(r'store\.LONGITUDE = \'(\d{1,4}\.\d{1,25})\';')
                lon = compLon.findall(btext)[0]
                # print u'{}, {}'.format(lat,lon)

                compTel = re.compile(r'store\.PHONE = "([\s\S]*?)";')
                tel = compTel.findall(btext)[0]
                # print tel

                if tel:
                    tel = telNormolize(tel)

                compTW = re.compile(r'store\.HOURS = "([\s\S]*?)";')
                timeW = re.sub(u'continuato', u'Ежедневно', compTW.findall(btext)[0])
                # print timeW

                jsAddr = {"#content": addr, "@lang": langv}
                jsName = {"#content": mainName, "@lang": langv}
                jsNameOth = {"#content": nameOth, "@lang": langv}
                jsCountry = {"#content": cantry, "@lang": langv}

                addresses.append(addr)

                jsTels = [{"number": mainPhone, "type": u"phone", "add_number": "", "info": ""}]
                if tel:
                    jsTels.append({"number": tel, "type": u"phone", "add_number": "", "info": ""})

                out = {
                    "url": mainUrl,
                    # "add-urls": addUrls,
                    "company-id": str(len(outData)+1),
                    "rubric_id": rubrics,
                    "name": jsName,
                    "name_other": jsNameOth,
                    "country": jsCountry,
                    "address": jsAddr,
                    "lat": lat,
                    "lon": lon,
                    "phone": jsTels,
                    "actualization-date": str(int(time()))
                }
                if timeW:
                    # print ('\n'+timeW)
                    locList = timeW.split('/')

                    if u':' not in locList[0] and u':' not in locList[1]:
                        timeW = u'{}:00/{}:00'.format(locList[0], locList[1])
                    timeW = re.sub('/', '-', timeW.strip())

                    jsWTime = {"#content": timeW, "@lang": langv}

                    out.update({"working_time": jsWTime})
                ischek = True
                for check in outData:
                    if check['address']['#content'] == out['address']['#content']:
                        ischek = False
                if ischek:
                    outData.append(out)
                    print(json.dumps(out, ensure_ascii=False).encode('utf-8'))
                #else:
                    #print ('not')
                    #print(json.dumps(out, ensure_ascii=False).encode('utf-8'))




addresses = []

if __name__ == '__main__':
    mainParse(u'https://ru.calzedonia.com/custserv/locate_store.cmd')
    # addressess=[]

    # for ad in allData:
    #     addressess.append(ad[1])
    #     addXML(ad[0], ad[1], ad[2], ad[3], ad[4], ad[5], ad[6], addressess.count(ad[1]))
    #
    # x = etree.tounicode(xml, pretty_print=True)
    #
    # print("<?xml version='1.0' encoding='utf-8'?>")
    # print(x.encode('utf-8'))
