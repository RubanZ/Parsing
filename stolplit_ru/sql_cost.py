# -*- coding: utf-8 -*-
import json

with open('out2.json') as json_file:  
    my_lines = json_file.readlines()
    l = 0
    for line in my_lines:
        data = json.loads(line)
        # st = "INSERT INTO `ke1b_site_tmplvar_contentvalues`(`tmplvarid`, `contentid`, `value`)" +\
        #     "VALUES(8," + str(3059 + l) + "," + json.dumps(data["cost"], ensure_ascii=False) + ");"
        st = "update `ke1b_site_tmplvar_contentvalues` set value=" + json.dumps(data["cost"], ensure_ascii=False) + " WHERE tmplvarid=8 and contentid=" + str(3059 + l) + ";"
        l+=1
        print st.encode('utf-8')