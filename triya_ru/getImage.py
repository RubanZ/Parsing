import requests
import json


with open('ot1.json') as f:
    for line in f:
        json_line = json.loads(line)

        res = requests.get('https://www.triya.ru' + json_line["image"], timeout=30)
        filename = 'D:\\OneDrive\\Projects\\Parsing\\triya_ru\\image\\' +json_line["image"].split("/")[-1]
        with open(filename, 'wb') as e:
            e.write(res.content)
        json_line["image"] = '/image/' + json_line["image"].split("/")[-1]
        #f.write(json.dumps(json_line, ensure_ascii=False).encode('utf-8'))