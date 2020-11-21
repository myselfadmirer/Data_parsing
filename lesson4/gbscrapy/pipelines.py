# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy import Request
from scrapy.exceptions import DropItem, CloseSpider
from scrapy.pipelines.images import ImagesPipeline


class GbscrapyPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['scrapy']

    def process_item(self, item, spider):
        collection = self.db[type(item).__name__]
        try:
            data = item['data']
            user_info = self.db.InstagramUserItem.find_one({'data.username': item['data']['username']})
            if not user_info:
                collection.insert_one(item)
                return item
            else:
                raise DropItem(f'The user already exists')
        except KeyError:
            # raise DropItem(f'relationship')
            try:
                path = item['path']
                while not item['start_user'] in path:
                    next_point = self.db.InstagramParentItem.find_one({'user': path[0]})
                    path.appendleft(next_point['parent_user'])
                item['path'] = list(path)
                print(item['path'])
                collection.insert_one(item)
                raise CloseSpider(reason='path is completed')
            except KeyError:
                collection.insert_one(item)
                return item


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



