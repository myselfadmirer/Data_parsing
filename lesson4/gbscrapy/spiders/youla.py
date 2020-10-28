import scrapy
from pymongo import MongoClient


class YoulaSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']
    xpath = {
        'brands': '//div[@class="TransportMainFilters_brandsList__2tIkv"]//a[@class="blackLink"]/@href',
        'ads': '//div[@id="serp"]//article//a[@data-target="serp-snippet-title"]/@href',
        'pagination': '//div[contains(@class, "Paginator_block")]/a/@href',
        'adv_title': '//div[contains(@class, "AdvertCard_advertTitle")]/text()',
        'adv_img': '//div[contains(@class, "PhotoGallery_block")]//img/@src',
        'adv_specification': '//div[contains(@class, "AdvertCard_specs")]//div/text()',
        'adv_description': '//div[contains(@class, "AdvertCard_descriptionInner")]/text()',
        'adv_seller_url': '',

    }
    db_client = MongoClient()

    def parse(self, response, **kwargs):
        for url in response.xpath(
                self.xpath['brands']):
            yield response.follow(url, callback=self.brand_parse)

    def brand_parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['pagination']):
            yield response.follow(url, callback=self.brand_parse)

        for url in response.xpath(self.xpath['ads']):
            yield response.follow(url, callback=self.ads_parse)

    def ads_parse(self, response, **kwargs):
        advert_dict = {'title': response.xpath(self.xpath['adv_title']).extract_first(),
                       'img_list': response.xpath(self.xpath['adv_img']).extract(),
                       'specification': response.xpath(self.xpath['adv_specification']).extract(),
                       'description': response.xpath(self.xpath['adv_description']).extract_first().replace('\n', '. '),
                       'seller': response.xpath('//div[contains(@class, "app_gridAsideChildren")]//'),
                       }
        self.save_to_db(advert_dict)

    def save_to_db(self, advert: dict):
        collection = self.db_client['scrapy_youla'][self.name]
        collection.insert_one(advert)

        print(1)
