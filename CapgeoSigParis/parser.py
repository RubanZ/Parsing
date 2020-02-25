# -*- coding: utf-8 -*-
import json
import re
import time
import requests
from lxml import etree

requests.urllib3.disable_warnings()


def CoordsConvert(x, y):
    return x, y


def GetFeeds():
    xml = etree.Element('companies')

    head = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "capgeo.sig.paris.fr",
        "Referer": "http://capgeo.sig.paris.fr/Apps/ParkingsParis/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    #url = "https://capgeo.sig.paris.fr/arcgis/rest/services/capgeo_dvd/DVD_Parcs_station_concedes/MapServer//dynamicLayer/query"
    url = "https://capgeo.sig.paris.fr/arcgis/rest/services/capgeo_dvd/DVD_Parcs_station_concedes/MapServer/4/query?where=&text=&objectIds=&time=&geometry=0%2C0%2C20037508.342789%2C20037508.342789&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=OBJECTID%2CID%2CNOM_PARC%2CADRESS_SSC%2CADRESS_GEO%2CACCES_VL%2CARRDT%2CDELEG%2CSITE_DELEG%2CTEL%2CH_PARC_CM%2CH2_PARC_CM%2CTYPE_PARC%2CHORAIRE_NA%2CASC_SURF%2CACCES_MOTO%2CACCES_VELO%2CV_ELEC_CH%2CAUTOPART%2CDATE_TA%2CAB_1M_E%2CAB_1A_E%2CTARIF_PR%2CPR_1A_MINE%2CPR_1A_MAXE%2CTARIF_RES%2CTF_RES_1AE%2CDATE_TH%2CTF_15MN_E%2CTF_30MN_E%2CTF_1H_E%2CTF_1H30_E%2CTF_2H_E%2CTF_3H_E%2CTF_4H_E%2CTF_7H_E%2CTF_8H_E%2CTF_9H_E%2CTF_10H_E%2CTF_11H_E%2CTF_12H_E%2CTF_24H_E%2CNB_PL_PMR%2CABPMR_1M_E%2CABPMR_1T_E%2CABPMR_1A_E%2CMIS_A_JOUR%2CABVE_1M_E%2CABVE_1T_E%2CABVE_1A_E%2CNB_PL_MOTO%2CTMOTO_1EHE%2CABMOTO_1ME%2CABMOTO_1TE%2CABMOTO_1AE%2CTVELO_1M_E%2CPOINT_X%2CPOINT_Y%2CZONES_RES%2CTF_15MN_MO%2CTF_30MN_MO%2CTF_24H_MOT%2CTF_PR_MOTO%2CPR_1A_MINM%2CPR_1A_MAXM%2CTF_RES_MO%2CTF_RES_1AM%2CAB_1A_PATT%2CPARC_AMOD%2CPARC_RELAI%2CAB_1M_RELA&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=+%7B%22wkid%22+%3A+4326%7D&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&resultOffset=&resultRecordCount=&f=pjson"
    tries = 0
    html = ""
    while tries < 20:
        try:
            html = requests.get(url, headers=head, verify=False, timeout=220)
            if html.status_code != requests.codes.ok:
                tries += 1
                continue
            html = html.text
            
            tries = 20
        except:
            tries += 1

    json_obj = json.loads(html)

    json_obj = json_obj["features"]
    ind = 1
    for obj in json_obj:
        lat, lon = CoordsConvert(obj["geometry"]["x"], obj["geometry"]["y"])

        work_time_text = obj["attributes"]["HORAIRE_NA"]
        work_time_text = work_time_text.replace("24h / 24", "0h / 24h")
        address_text = obj["attributes"]["ADRESS_GEO"].title()
        phone_text = obj["attributes"]["TEL"]
        phone_text = phone_text.replace('.', ' ')
        if not re.match('\d\d \d\d \d\d \d\d \d\d', phone_text):
            phone_text = ''
        name_text = obj["attributes"]["NOM_PARC"].title() + " (" + obj["attributes"]["DELEG"].title() + ")"

        price_text = \
            u"15 min = " + obj["attributes"]["TF_15MN_E"] + u" €; " \
            + u"30 min = " + obj["attributes"]["TF_30MN_E"] + u" €; " \
            + u"1 h = " + obj["attributes"]["TF_1H_E"] + u" €; " \
            + u"1 h 30 = " + obj["attributes"]["TF_1H30_E"] + u" €; " \
            + u"2 h = " + obj["attributes"]["TF_2H_E"] + u" €; " \
            + u"4 h = " + obj["attributes"]["TF_4H_E"] + u" €; " \
            + u"8 h = " + obj["attributes"]["TF_8H_E"] + u" €; " \
            + u"12 h = " + obj["attributes"]["TF_12H_E"] + u" €; " \
            + u"24 h = " + obj["attributes"]["TF_24H_E"] + u" €"

        company = etree.Element("company")
        etree.SubElement(company, "company-id").text = str(ind)
        ind += 1

        nam = etree.SubElement(company, "name")
        nam.text = u'Parking ' + name_text
        nam.set("lang", "fr")

        etree.SubElement(company, "rubric-id").text = '184105270'

        con = etree.SubElement(company, "country")
        con.text = u"Франция"
        con.set("lang", "ru")

        address = etree.SubElement(company, "address")
        address.text = address_text + u", Paris, France"
        address.set("lang", "fr")

        work_time = etree.SubElement(company, "working-time")
        work_time.text = work_time_text
        work_time.set("lang", "fr")

        etree.SubElement(company, "actualization-date").text = str(int(time.time()))

        if phone_text != '':
            phone = etree.SubElement(company, "phone")
            etree.SubElement(phone, "ext")
            etree.SubElement(phone, "type").text = "phone"
            etree.SubElement(phone, "number").text = phone_text
            etree.SubElement(phone, "info")

        coord = etree.SubElement(company, "coordinates")

        etree.SubElement(coord, "lon").text = str(lon)
        etree.SubElement(coord, "lat").text = str(lat)

        paid_bool = (re.search(u"\d+?,\d+? €", price_text) != None)

        if (paid_bool):
            ext = etree.SubElement(company, "feature-enum-multiple")
            ext.set("name", "type_parking")
            ext.set("value", "paid_parking")
        else:
            ext = etree.SubElement(company, "feature-enum-multiple")
            ext.set("name", "type_parking")
            ext.set("value", "free_parking")

        if (paid_bool):
            ext = etree.SubElement(company, "feature-text-single")
            ext.set("name", "parking_price")
            ext.set("value", price_text)

        xml.append(company)

    out = (etree.tostring(xml, pretty_print=True, xml_declaration=True, encoding="UTF-8").replace(
        "<?xml version='1.0' encoding='UTF-8'?>", '<?xml version="1.0" encoding="UTF-8"?>'))
    out = re.sub("^\s*", "", out)
    print out


GetFeeds()
