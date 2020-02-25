import requests
import json


with open('out.json') as f:
    for line in f:
        json_line = json.loads(line)

        # res = requests.get('https://www.stolplit.ru' + json_line["mainImage"], timeout=30)
        # filename = 'D:\\OneDrive\\Projects\\Parsing\\stolplit_ru\\image\\' +json_line["mainImage"].split("/")[-1]
        # with open(filename, 'wb') as e:
        #     e.write(res.content)

        for item in json_line["image"]:
            print(json_line["image"][item])
            res2 = requests.get('https://www.stolplit.ru' + json_line["image"][item], timeout=30)

            filename2 = 'D:\\OneDrive\\Projects\\Parsing\\stolplit_ru\\image\\' +json_line["image"][item].split("/")[-1]

            with open(filename2, 'wb') as e2:
                e2.write(res2.content)