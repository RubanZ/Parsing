# -*- coding: utf-8 -*-

import json

catalog = []

with open('ot1.json') as json_file:  
    my_lines = json_file.readlines()
    for line in my_lines:
        my_json = json.loads(line)

        append = True

        for n in catalog:
            if my_json['catalog'] == n:
                append = False
                break
        if append:
            catalog.append(my_json['catalog'])


print(catalog)