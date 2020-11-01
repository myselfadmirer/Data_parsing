import scrapy
from ..loaders import YoulaAutoLoader


class YoulaSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/moskva/']
    xpath = {
        'brands': '//div[@class="TransportMainFilters_brandsList__2tIkv"]//a[@class="blackLink"]/@href',
        'ads': '//div[@id="serp"]//article//a[@data-target="serp-snippet-title"]/@href',
        'pagination': '//div[contains(@class, "Paginator_block")]/a/@href',
    }

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
        loader = YoulaAutoLoader(response=response)
        url = loader.add_value('url', response.url)
        title = loader.add_xpath('title', '//div[contains(@class, "AdvertCard_advertTitle")]/text()')
        img_list = loader.add_xpath('img_list', '//div[contains(@class, "PhotoGallery_block")]//img/@src')
        specifications = loader.add_xpath('specifications',
                                          '//div[contains(@class, "AdvertCard_specs")]//div[contains(@class, '
                                          '"AdvertSpecs")]')
        description = loader.add_xpath('description', '//div[contains(@class, "AdvertCard_descriptionInner")]/text()')
        seller = loader.add_xpath('seller', '//script[contains(text(), "window.transitState =")]/text()')
        phone_number = loader.add_xpath('phone_number',
                                        '//script[contains(text(), "window.transitUserData = decodeURIComponent")]/text()')
        yield loader.load_item()


print(1)
