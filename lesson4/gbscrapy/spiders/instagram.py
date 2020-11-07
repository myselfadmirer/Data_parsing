import scrapy
import json
from datetime import datetime
from items import InstagramPostItem, InstagramTagItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    query_hash = '9b498c08113f1e09617a1703c22b2f32'
    query_url = 'https://www.instagram.com/graphql/query/'

    def __init__(self, login, enc_password, *args, **kwargs):
        self.tags = ['cat']
        self.login = login
        self.enc_password = enc_password
        super().__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.login,
                    'enc_password': self.enc_password,
                },
                headers={
                    'X-CSRFToken': js_data['config']['csrf_token']
                }
            )
        except AttributeError as e:
            if response.json().get('authenticated'):
                for tag in self.tags:
                    yield response.follow(f'/explore/tags/{tag}/', callback=self.tag_parse, cb_kwargs={'param': tag})

    def tag_parse(self, response, **kwargs):
        tag_data = self.js_data_extract(response)['entry_data']['TagPage'][0]['graphql']['hashtag']
        yield InstagramTagItem(date_parse=datetime.now(), data={'id': tag_data['id'],
                                                                'name': tag_data['name'],
                                                                'pic_url': tag_data['profile_pic_url'],
                                                                })
        yield from self.get_tag_info_parse(response, tag_data)

    def get_tag_info_parse(self, response, tag_data):
        if tag_data['edge_hashtag_to_media']['page_info']['has_next_page']:
            end_cursor = tag_data['edge_hashtag_to_media']['page_info']['end_cursor']
            variables = {
                "tag_name": tag_data['name'],
                "first": 100,
                "after": end_cursor
            }
            pagination = f'{self.query_url}?query_hash={self.query_hash}&variables={json.dumps(variables)}'
            yield response.follow(pagination, callback=self.get_pagination_parse)

        yield from self.get_post_info_parse(tag_data['edge_hashtag_to_media']['edges'])

    def get_pagination_parse(self, response, **kwargs):
        yield from self.get_tag_info_parse(response, response.json()['data']['hashtag'])

    @staticmethod
    def get_post_info_parse(edges):
        for node in edges:
            yield InstagramPostItem(date_parse=datetime.now(),
                                    data=node['node'], )

    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData = ")]/text()').get()
        return json.loads(script.replace('window._sharedData = ', '')[:-1])
