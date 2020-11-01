from typing import Any, Union

from scrapy import Selector
import re
from itemloaders.processors import TakeFirst, MapCompose
from scrapy.loader import ItemLoader
from .items import YoulaAutoItem, HhRemoteItemEmployer, HhRemoteItemVacancy


def search_seller(itm):
    re_str = re.compile(r'youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar')
    result = re.findall(re_str, itm)
    return result


def create_user_url(itm):
    base_url = 'https://youla.ru/user/'
    result = base_url + itm
    return result


def get_specifications(itm):
    tag = Selector(text=itm)
    return {tag.xpath('//div/div[1]/text()').get(): tag.xpath('//div/div[2]/text()').get() or tag.xpath(
        '//div/div[2]/a/text()').get()}


def get_specifications_out(itms):
    result = {}
    for itm in itms:
        if None not in itm:
            result.update(itm)
    return result


def get_description(items):
    pass


def get_phone_number(itm):
    print(1)


def get_phone_number_out(itm):
    pass


class YoulaAutoLoader(ItemLoader):
    default_item_class = YoulaAutoItem
    seller_in = MapCompose(search_seller, create_user_url)
    seller_out = TakeFirst()
    title_out = TakeFirst()
    specifications_in = MapCompose(get_specifications)
    specifications_out = get_specifications_out
    description_out = TakeFirst()
    url_out = TakeFirst()
    phone_number_in = MapCompose(get_phone_number)
    phone_number_out = get_phone_number_out


def get_activities_out(itm):
    if ',' in itm:
        itm = itm.split(',')
    return itm


def get_employer_url(itm):
    base_url = 'https://hh.ru'
    result = base_url + itm
    return result


class HhRemoteLoaderVacancy(ItemLoader):
    default_item_class = HhRemoteItemVacancy

    """vacancy"""
    url_out = TakeFirst()
    name_out = TakeFirst()
    salary_in = ''.join
    salary_out = TakeFirst()
    description_in = ''.join
    description_out = TakeFirst()
    employer_url_in = MapCompose(get_employer_url)
    employer_url_out = TakeFirst()


class HhRemoteLoaderEmployer(ItemLoader):
    default_item_class = HhRemoteItemEmployer

    """employer"""
    url_out = TakeFirst()
    name_in = ''.join
    name_out = TakeFirst()
    employer_url_out = TakeFirst()
    areas_of_activity_in = MapCompose(get_activities_out)
    # areas_of_activity_out = TakeFirst()
    description_in = ''.join
    description_out = TakeFirst()
    print(2)
