# -*- coding: utf-8 -*-
import json

with open('out2.json') as json_file:  
    my_lines = json_file.readlines()
    l = 0
    for line in my_lines:
        data = json.loads(line)
        sss = '{"fieldValue":['
        for item in data["image"]:
            sss += '{"image": "' + data["image"][item] + '", "thumb":"","title":""},'

        sss += '{"image":"' + data["mainImage"] + '","thumb":"","title":""}],"fieldSettings":{"autoincrement":1}}'
        
        st = "INSERT INTO `ke1b_site_tmplvar_contentvalues`(`tmplvarid`, `contentid`, `value`)" +\
            "VALUES(7," + str(3059 + l) + ",'" + sss + "');"
        l+=1
        print st.encode('utf-8')



