import scrapy
import json


class IngredientsSpider(scrapy.Spider):
    name = "ingredients"

    def start_requests(self):
        file = 'result.json'
        result_file = 'ingredients.json'
        self.log(file)

        start_index = 0

        with open(file, "r", encoding='utf-8') as text_file:
            for line in text_file:
                js_file = json.loads(line)

                for ingredient in js_file['ingredients']:
                    ingredient_js = json.loads(ingredient)
                    result = {
                        "name": ingredient_js['name'],
                        "amount": "единица измерения",
                        "data": []
                    }
                    start_index+=1
                    with open(result_file, "a", encoding='utf-8') as text_file:
                        print(json.dumps(result, ensure_ascii=False),
                              file=text_file)

        # with open(result_file, "r+", encoding='utf-8') as f:
        #     lines = f.readlines()
        #     lines.sort()
        #     f.seek(0)
        #     f.writelines(lines)
    #     url = "https://eda.ru/recepty/ingredienty/"
    #     start_index = 13405

    #     while True:
    #         start_index += 1
    #         yield scrapy.Request(method="GET", url=url + str(start_index), meta={"index": start_index}, callback=self.parse)

    # def save_result(self, response):
    #     item = response.meta["index"]

    #     with open(result_file, "a", encoding='utf-8') as text_file:
    #         print(json.dumps(ingredient, ensure_ascii=False), file=text_file)
