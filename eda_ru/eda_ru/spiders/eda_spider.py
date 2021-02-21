import scrapy
import json
from bs4 import BeautifulSoup


class EdaSpider(scrapy.Spider):
    name = "eda"
    hasMore = False
    recipes = 0

    def start_requests(self):
        url = 'https://eda.ru/RecipesCatalog/GetNextRecipesDesktop'

        hasMore = True

        while hasMore:
            self.recipes += 1
            self.log(self.recipes)
            headers = {"Content-Type": "application/json"}
            body_req = '{"page": ' + str(self.recipes) + ' }'
            yield scrapy.Request(method="POST", url=url, body=body_req, headers=headers ,callback=self.parse)

    def parse(self, response):
        data = json.loads(response.text)
        soup = BeautifulSoup(data['Html'], 'html.parser')
        title =  soup.select('div[class=clearfix]')
        for elem in title:
            
            result = {
                "title": elem.select_one('div[data-title]').get('data-title'),
                "category": self.type_recipes(elem),
                "img": elem.select_one('div[data-title]').get('data-src'),
                "prep-time": self.prep_time_parse(elem),
                "portions": self.portions_parse(elem),
                "ingredients": self.ingredients_list(elem),
                "author" : self.author_parse(elem),
                "link": self.link_parse(elem)
            }
            with open("result.json", "a", encoding='utf-8') as text_file:
                print(json.dumps(result, ensure_ascii=False), file=text_file)

        self.log(f'Saved file')

    def type_recipes(self, data):
        '''
        <div class='horizontal-tile__item-link js-click-link '
            data-href="/recepty/zavtraki/sirniki-iz-tvoroga-18506">
            <div class="lazy-load-container js-lazy-loading" data-title="Сырники из творога"
                data-alt="Сырники из творога"
                data-src="https://eda.ru/img/eda/c285x285i/s2.eda.ru/StaticContent/Photos/120213175531/180415114517/p_O.jpg">
            </div>
        </div>
        '''
        if (data.select_one('div[data-href*="zavtraki"]') is not None):
            return "Завтраки"
        elif (data.select_one('div[data-href*="vypechka-deserty"]') is not None):
            return "Выпечка и десерты"
        elif (data.select_one('div[data-href*="osnovnye-blyuda"]') is not None):
            return "Основные блюда"
        elif (data.select_one('div[data-href*="salaty"]') is not None):
            return "Салаты"
        elif (data.select_one('div[data-href*="supy"]') is not None):
            return "Супы"
        elif (data.select_one('div[data-href*="pasta-picca"]') is not None):
            return "Паста и пицца"
        elif (data.select_one('div[data-href*="zakuski"]') is not None):
            return "Закуски"
        elif (data.select_one('div[data-href*="sendvichi"]') is not None):
            return "Сэндвичи"
        elif (data.select_one('div[data-href*="napitki"]') is not None):
            return "Напитки"
        elif (data.select_one('div[data-href*="bulony"]') is not None):
            return "Бульоны"
        else:
            return "Другое"

    def ingredients_list(self, data):
        '''
        <p class="ingredients-list__content-item content-item js-cart-ingredients"
            data-ingredient-object='{"id": 13418, "name": "Куриное яйцо", "amount": "2 штуки"}'>
            <span class="content-item__name tooltip">
                <span class="js-tooltip js-tooltip-ingredient"
                    data-url="/Ingredient/RecipePreview" data-id="13418">
                    Куриное яйцо
                </span>
            </span>
            <span class="content-item__measure js-ingredient-measure-amount" data-id="13418">2
                штуки</span>
        </p>
        '''
        ingredients = data.select('[class~=ingredients-list__content-item]')
        result = []
        for ingredient in ingredients:
            result.append(ingredient.get('data-ingredient-object'))
        return result    

    def author_parse(self, data):
        '''
        <div class="horizontal-tile__author">
            Автор: <span class="horizontal-tile__author-link js-click-link" data-href="https://eda.ru/avtory/210134"
                content="Алексей Скобелев">Алексей Скобелев</span>
        </div>
        '''
        author = data.select_one('[class~=horizontal-tile__author-link]')
        return {
            "author": author.get('content'),
            "link": author.get('data-href'),
            "source": "eda.ru"
        }

    def link_parse(self, data):
        '''
        <div class='horizontal-tile__item-link js-click-link '
                data-href="/recepty/zavtraki/sirniki-iz-tvoroga-18506">
        '''
        link = data.select_one('[class~=horizontal-tile__item-link]')
        return "https://eda.ru" + link.get('data-href')
    
    def prep_time_parse(self, data):
        try:
            msg = data.select_one('[class~=prep-time]').get_text()
            msg = msg.replace("\n\n\n\r\n            ", "")
            msg = msg.replace("\r\n\r\n          ", "")
            return msg
        except:
            return None
    def portions_parse(self, data):
        try:
            msg = data.select_one('[class~=js-portions-count-print]').get_text()
            msg = msg.replace("\r\n            ", "")
            msg = msg.replace("\r\n          ", "")
            if (msg.find(" порции") > -1):
                msg = msg.replace(" порции", "")
            if (msg.find(" порция") > -1):
                msg = msg.replace(" порция", "")
            if (msg.find(" порций") > -1):
                msg = msg.replace(" порций", "")
            return msg
        except:
            return None