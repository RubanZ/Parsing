# coding=utf-8
import json
import re
import sys
import time
import requests
from argparse import ArgumentParser
from lxml import etree
from lxml.html import fromstring


main_country = u'Türkiye'
main_phones = ['+90 (850) 222-06-00']
main_wh = u'Hafta içi 09:00 - 17:00 öğle tatili 12:30-13:30'
main_host = 'https://www.ingbank.com.tr'

add_urls = ['https://www.facebook.com/ingbankturkiye', 'https://twitter.com/ingbankturkiye']
xml = etree.Element('companies')


def addXML(id, other_name, addr, lat, lon, ph, fx):
    company = etree.Element('company')
    etree.SubElement(company, 'company-id').text = id
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

    for mph in main_phones:
        phone = etree.SubElement(company, 'phone')
        etree.SubElement(phone, 'ext')
        etree.SubElement(phone, 'type').text = 'phone'
        etree.SubElement(phone, 'number').text = mph
        etree.SubElement(phone, 'info')

    if ph:
        phone = etree.SubElement(company, 'phone')
        etree.SubElement(phone, 'ext')
        etree.SubElement(phone, 'type').text = 'phone'
        etree.SubElement(phone, 'number').text = ph
        etree.SubElement(phone, 'info')

    if fx:
        fax = etree.SubElement(company, 'phone')
        etree.SubElement(fax, 'ext')
        etree.SubElement(fax, 'type').text = 'fax'
        etree.SubElement(fax, 'number').text = fx
        etree.SubElement(fax, 'info')

    if type == 'branch':
        working_time = etree.SubElement(company, 'working-time')
        working_time.text = main_wh
        working_time.set('lang', 'tr')

    coordinates = etree.SubElement(company, 'coordinates')
    lt = etree.SubElement(coordinates, 'lat')
    lt.text = str(lat)
    ln = etree.SubElement(coordinates, 'lon')
    ln.text = str(lon)

    etree.SubElement(company, 'actualization-date').text = str(int(time.time()))

    xml.append(company)

def normalizeAddress(address):
    address = re.sub(
        u'(\s(mahalle\s|mahallesi\s|mah\s|mh\s|mah\.|mh\.|cadde\s|caddesi\s|cad\s|cad\.|cd\.|sokak\s|sokağı\s|sok\.|sk\.))\s?(\w)',
        '\g<1>, \g<3>', address, flags=re.U | re.I | re.UNICODE)
    address = re.sub('\s,', ',', address)

    address = re.sub('(\w)\.(\w)', '\g<1>. \g<2>', address, flags=re.UNICODE)

    address = ' '.join(address.split()).title().strip()

    address = re.sub('(No?\s?:\s?[\d\s\-/\w]+?)(\s([^\W\d][^\W\d])+)', '\g<1>,\g<2>', address,
                     flags=re.UNICODE)  # comma after No:...
    address = re.sub('([^\d\s:][^\d\s])(\s?//?\s?)', '\g<1>, ', address)

    return address

def normalizePhone(phone):
    phone = phone.strip()
    if not phone or phone == '-':
        return None

    phone = re.sub('\D', '', phone)
    phone = re.sub('^0', '', phone)
    phone = re.sub('^90', '', phone)

    country_code = '+90'
    code, number = phone[:3], phone[3:]
    number = number[:3] + ' ' + number[3:5] + ' ' + number[-2:]
    phone = country_code + ' (' + code + ') ' + number

    return phone


def read_argument():
    argp = ArgumentParser()
    argp.add_argument('--type', type=str, required=True, help='branch | atm')
    args = argp.parse_args()
    return args.type

if __name__ == '__main__':
    global main_name, rubric

    type = read_argument()
    
    
    if type == 'branch':
        rubric = '184105398'
        main_name = u'ING Bank Şubesi'
    elif type == 'atm':
        rubric = '184105402'
        main_name = u'ING Bank ATM'
    else:
        sys.stderr.write('Wrong type. See -h.')
        exit()


    response = requests.get('https://www.ing.com.tr/tr/bilgi-destek/sube-ve-atm-bulucu')
    data = fromstring(response.text).xpath('//select[@id="ddlCity"]/option/@value')
    count = 0
    for city in data:
        atm = requests.post('https://www.ing.com.tr/ProxyManagement/SiteManagerService_Script.aspx/ListBranchAndATM', json={"CityTitle":city,"TownTitle":"","BranchNumberOrLocation":"","SearchTextDataHolder":"Ara...","ForeignExchange":"","SightlessDisabledPrp":"","PhsycaldisabledPrp":""})
        json_data = json.loads(json.loads(atm.text)['d'])
        if atm.text.encode('utf-8') != '{"d":"[]"}':
            for item in json_data:
                if type == 'branch' and item['info']['isATM'] == False:
                    count+=1
                    address = fromstring(response.text).xpath('//select[@id="ddlCity"]/option[@value="' + city + '"]/text()')[0] + ', ' + normalizeAddress(item['info']['address'])
                    addXML(str(count), item['info']['name'], address, item['maps']['lat'], item['maps']['lng'], normalizePhone(item['info']['phone']), item['info']['fax'])
                if type == 'atm' and item['info']['isATM'] == True:
                    count+=1
                    address = fromstring(response.text).xpath('//select[@id="ddlCity"]/option[@value="' + city + '"]/text()')[0] + ', ' + normalizeAddress(item['info']['address'])
                    addXML(str(count), item['info']['name'], address, item['maps']['lat'], item['maps']['lng'], normalizePhone(item['info']['phone']), item['info']['fax'])
       

            
    
    x = etree.tounicode(xml, pretty_print=True)
    print("<?xml version='1.0' encoding='utf-8'?>")
    print(x.encode('utf-8'))