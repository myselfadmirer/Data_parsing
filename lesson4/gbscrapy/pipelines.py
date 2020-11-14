# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline


class GbscrapyPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['scrapy']

    def process_item(self, item, spider):
        collection = self.db[type(item).__name__]
        try:
            item['data'] and self.db.InstagramUserItem.find({'data': {'username': item['data']['username']}})
        except KeyError:
            collection.insert_one(item)
            return item
        return True


class GbscrapyImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        images = item.get('pic_url',
                          item['data'].get('profile_pic_url',
                                           item['data'].get('display_url',
                                                            [])))
        if not isinstance(images, list):
            images = [images]
        for url in images:
            try:
                yield Request(url)
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        try:
            item['pic_url'] = [item[1] for item in results if item[0]]
        except KeyError:
            pass
        return item

#
# class GbscrapyCheckPipeline:
#     def __init__(self):
#         client = MongoClient('localhost', 27017)
#         self.db = client['scrapy']



