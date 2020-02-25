# -*- coding: utf-8 -*-
import time
import uuid

#catalog = [u'Модульные гостиные', u'Матрасы двуспальные', u'Гостиные гарнитуры', u'Стеллажи', u'Компьютерные столы ', u'Размер 140х200', u'Детские столы', u'Кровати', u'Детские кровати', u'Спальни', u'Размер 120х200', u'Размер 160х200', u'Размер 180х200', u'Мебель для ТВ', u'Пуфы', u'Доводчики и подсветка', u'Настенные зеркала', u'Обувницы', u'Вешалки', u'Вешалки и зеркала', u'Комоды', u'Готовые наборы офисной мебели', u'Журнальные столики', u'Шкафы для спальни', u'Модульная офисная мебель', u'Офисные тумбы', u'Табуреты', u'Готовые уголки', u'Обеденные группы', u'Офисные столы', u'Шкафы для прихожей', u'Офисные шкафы', u'Шкафы для гостиной', u'Шкафы для детской', u'Полки настенные', u'Лофт', u'Комоды для детской', u'Угловые скамьи', u'Кухонные стулья', u'Кухонные столы', u'Столы для уголков', u'Столы и стулья', u'Плинтусы и цоколи', u'Столешницы и пристенные панели', u'Шкафы кухонные', u'Готовые кухонные гарнитуры', u'Модульная мебель для кухни', u'Готовые наборы', u'Модульная мебель для прихожей', u'Шкафы-купе 160 см', u'Зеркала', u'Наполнение', u'Шкафы-купе 180 см', u'Шкафы-купе 120 см', u'Размер 90х200', u'Размер 80х200', u'Шкафы-купе 140 см', u'Шкафы-купе', u'Готовые спальные гарнитуры', u'Туалетные столики и трюмо', u'Модульная мебель для спальни', u'Прикроватные тумбы', u'Тумбы для детской', u'Готовые детские наборы', u'Модульные детские', u'Диваны', u'Кресла и пуфы', u'Мягкая мебель']
catalog = [u'Кухонные гарнитуры', u'Табуреты', u'Обеденные группы', u'Дополнительно', u'Кухонные мойки', u'Мойки, сушки, смесители для кухни', u'Ортопедические основания', u'Комплектующие', u'Гретта', u'Джорджия', u'Персей', u'Дакота Венге/Ваниль', u'Шкафы', u'Симба софт', u'Лас Вегас', u'Монако', u'Витрины', u'Илона', u'Клео', u'Версаль (Белый Ясень)', u'Стеллажи', u'Дакота', u'Сити', u'Открытые', u'Ника', u'Верди', u'Шкафы-купе', u'Обувницы', u'Мамбо', u'Тумбы', u'Афина', u'Медея', u'Полки для гостиной', u'Комоды', u'Обеденные зоны', u'Аксессуары для кухни', u'Угловые шкафы', u'Шкафы распашные', u'Гретта (дуб-феррара)', u'Зеркала', u'Настенные', u'Прихожие', u'Сидней', u'Напольные', u'Закрытые', u'Вешалки', u'Марсель', u'Мелисса', u'Амели', u'Корпуса', u'Шкафы пеналы', u'Терра', u'Ангелина', u'1400 x 2000', u'900 x 2000', u'Туалетные столики', u'1600 x 2000', u'800 x 2000', u'Декор для кабинета', u'Дионис', u'Прямые', u'Компьютерные', u'Угловые', u'Прямые компьютерные столы', u'Компьютерные столы', u'Дакота белая', u'Детские стеллажи и полки', u'Маугли', u'Денди', u'Венеция', u'Кровати одноярусные', u'Кровати двухъярусные', u'Детские кровати', u'Матрасы 80 см', u'800 x 1900', u'Матрасы 90 см', u'Матрасы 140 см', u'900 x 1900', u'Детские комоды', u'Матрасы 160 см', u'Письменные', u'Прикроватные тумбы', u'Наматрасники', u'Кристина', u'Кровати 160 см', u'Двуспальные', u'Мишель', u'Кровати 140 см', u'Односпальные', u'Журнальные', u'Журнальные столики', u'ТВ-тумбы', u'Стенки для гостиной', u'Пуф без ящика', u'Банкетка', u'Столешницы', u'Стеновые панели']

# for i in catalog:
#     print(catalog.index(i)+2272)


for c in catalog:
    st = "INSERT INTO `ke1b_site_content`(`pagetitle`,`alias`,`parent`,`content`,`createdon`,`type`,`contentType`,`published`,`richtext`,`template`,`menuindex`,`searchable`,`cacheable`,`createdby`,`editedby`,`publishedby`,`donthit`,`privateweb`,`privatemgr`,`content_dispo`,`hidemenu`,`alias_visible`,`publishedon`, `isfolder`)"+\
        " VALUES("+"'"+c+"'"+","+"'"+str(uuid.uuid4())+"'"+","+"'"+str(8)+"'"+","+"'"+""+"'"+","+str(int(time.time()))+\
        ",'document','text/html',1,1,7,0,1,1,7,7,7,0,0,0,0,0,1,"+str(int(time.time()))+\
        ",1);"
    print st.encode('utf-8')