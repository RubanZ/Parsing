# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

class BccKzPipeline(object):
    def __init__(self):
        self.na = []  # names, addresses

    def process_item(self, item, spider):
        # print(item['address']['#content'].encode('utf-8'))
        # raise Exception()
        na = item['name']['#content'] + item['address']['#content']
        self.na.append(na)
        item['company-id'] = self.na.count(na)
        return item
