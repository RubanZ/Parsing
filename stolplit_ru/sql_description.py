# -*- coding: utf-8 -*-
import json


with open('ot1.json') as json_file:  
    my_lines = json_file.readlines()
    l = 0
    for line in my_lines:
        data = json.loads(line)
        sss = '{"fieldValue":['
        for item in data["properties"]:
            sss += '{"key": "' + item + '" , "value": "' + data["properties"][item] + '"},'
        sss = sss[:-1]
        sss += '],"fieldSettings":{"autoincrement":1}}'    
        st = "INSERT INTO `ke1b_site_tmplvar_contentvalues`(`tmplvarid`, `contentid`, `value`)" +\
            "VALUES(10," + str(3059 + l) + ",'" + sss + "');"
        l+=1
        print st.encode('utf-8')



#{"fieldValue":[{"key":"аа","value":"ыыы"}],"fieldSettings":{"autoincrement":1}}