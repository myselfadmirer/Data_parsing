# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GbscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class YoulaAutoItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    img_list = scrapy.Field()
    specifications = scrapy.Field()
    description = scrapy.Field()
    seller = scrapy.Field()


class HhRemoteItemVacancy(scrapy.Item):
    """vacancy"""
    _id = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    employer_url = scrapy.Field()


class HhRemoteItemEmployer(scrapy.Item):
    """employer"""
    _id = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    employer_url = scrapy.Field()
    areas_of_activity = scrapy.Field()
    description = scrapy.Field()


class InstagramItem(scrapy.Item):
    _id = scrapy.Field()
    id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    pic_url = scrapy.Field()


class InstagramPostItem(InstagramItem):
    """post data"""
    pass


class InstagramTagItem(InstagramItem):
    """tag data"""
    pass


class InstagramUserItem(InstagramItem):
    """user data"""


class InstagramFollowersItem(scrapy.Item):
    """followers"""
    _id = scrapy.Field()
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    follower_id = scrapy.Field()
    follower_name = scrapy.Field()


class InstagramFollowingItem(scrapy.Item):
    """following"""
    _id = scrapy.Field()
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    following_id = scrapy.Field()
    following_name = scrapy.Field()


class InstagramPathItem(scrapy.Item):
    _id = scrapy.Field()
    start_user = scrapy.Field()
    target_user = scrapy.Field()
    path = scrapy.Field()
