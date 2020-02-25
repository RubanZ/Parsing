# -*- coding: utf-8 -*-
import json

with open('out2.json') as json_file:  
    my_lines = json_file.readlines()
    l = 0
    for line in my_lines:
        data = json.loads(line)
        st = "INSERT INTO `ke1b_site_tmplvar_contentvalues`(`tmplvarid`, `contentid`, `value`)" +\
            "VALUES(9," + str(378 + l) + "," + json.dumps(data["cost"], ensure_ascii=False) + ");"
        l+=1
        if l == 1:
            l+=1
        print st.encode('utf-8')