# -*- coding: utf-8 -*-
import json

with open('ot1.json') as json_file:  
    my_lines = json_file.readlines()

with open('out.json') as js2_file:
    my_lines2 = js2_file.readlines()
    
   
for line in my_lines:
    error_json = json.loads(line)

    for line2 in my_lines2:
        norm_json = json.loads(line2)
        
        if (error_json['name'] == norm_json['name']):
            error_json['mainImage'] = '/assets/images/' + norm_json['mainImage'].split("/")[-1]
    
    print(json.dumps(error_json, ensure_ascii=False).encode('utf-8'))

        