import scrapy
import json
from datetime import datetime
from collections import deque
from items import InstagramPostItem, InstagramTagItem, InstagramUserItem, InstagramFollowersItem, \
    InstagramFollowingItem, InstagramPathItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    tag_query_hash = '9b498c08113f1e09617a1703c22b2f32'
    followers_query_hash = 'c76146de99bb02f6415203be841dd25a'
    following_query_hash = 'd04b0a864b4b54837c0d870b0e77e076'
    query_url = 'https://www.instagram.com/graphql/query/'

    def __init__(self, login, enc_password, *args, **kwargs):
        self.tags = ['cat']
        self.start_user = 'myself_admirer'
        self.target_user = ''
        self.users_deque = deque([self.start_user])
        self.login = login
        self.enc_password = enc_password
        self.path = []
        self.followers_set = set()
        self.following_set = set()
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
                # for tag in self.tags:
                #     yield response.follow(f'/explore/tags/{tag}/', callback=self.tag_parse, cb_kwargs={'param': tag})
                while self.users_deque:
                    user = self.users_deque.pop()
                    self.followers_set.clear()
                    self.following_set.clear()
                    yield response.follow(f'/{user}/', callback=self.user_info_parse,
                                          cb_kwargs={'param': user, })

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
            pagination = f'{self.query_url}?query_hash={self.tag_query_hash}&variables={json.dumps(variables)}'
            yield response.follow(pagination, callback=self.get_pagination_parse, cb_kwargs={'param': 'hashtag'})

        yield from self.get_post_info_parse(tag_data['edge_hashtag_to_media']['edges'])

    @staticmethod
    def get_post_info_parse(edges):
        for node in edges:
            yield InstagramPostItem(date_parse=datetime.now(),
                                    data=node['node'], )

    """pagination"""

    def get_pagination_parse(self, response, **kwargs):
        yield from self.get_tag_info_parse(response, response.json()['data'][kwargs['param']])

    """json extract data"""

    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData = ")]/text()').get()
        return json.loads(script.replace('window._sharedData = ', '')[:-1])

    def user_info_parse(self, response, **kwargs):
        user_data = self.js_data_extract(response)['entry_data']['ProfilePage'][0]['graphql']['user']
        item = yield InstagramUserItem(date_parse=datetime.now(), data=user_data, )
        if isinstance(item, str):
            print(item)
            pass
        else:
            """followers"""
            yield from self.get_api_followers_following_parse(response, user_data, self.followers_query_hash,
                                                              'edge_followed_by')
            '''following'''
            yield from self.get_api_followers_following_parse(response, user_data, self.following_query_hash,
                                                              'edge_follow')

    def get_api_followers_following_parse(self, response, user_data, query_hash, edge, variables=None):
        if not variables:
            variables = {
                'id': user_data['id'],
                'first': 100,
            }
        api_url = f'{self.query_url}?query_hash={query_hash}&variables={json.dumps(variables)}'
        yield response.follow(api_url, callback=self.followers_following_parse, cb_kwargs={'user_data': user_data,
                                                                                           'edge': edge,
                                                                                           'query_hash': query_hash,
                                                                                           })

    def followers_following_parse(self, response, **kwargs):
        if b'application/json' in response.headers['Content-Type']:
            api_data = response.json()
            yield from self.get_follow_item(kwargs['user_data'], api_data['data']['user'], kwargs['edge'])
            if api_data['data']['user'][kwargs['edge']]['page_info']['has_next_page']:
                end_cursor = api_data['data']['user'][kwargs['edge']]['page_info']['end_cursor']
                variables = {
                    'id': kwargs['user_data']['id'],
                    'first': 100,
                    'after': end_cursor,
                }
                yield from self.get_api_followers_following_parse(response, kwargs['user_data'], kwargs['query_hash'],
                                                                  kwargs['edge'], variables)
            else:
                return self.get_result_set(kwargs['user_data']['username'])

    def get_follow_item(self, user_data, follow_data, edge):
        for user in follow_data[edge]['edges']:
            if edge == 'edge_followed_by':
                """followers"""
                self.followers_set.add(user['node']['username'])
                yield InstagramFollowersItem(
                    user_id=user_data['id'],
                    user_name=user_data['username'],
                    follower_id=user['node']['id'],
                    follower_name=user['node']['username'],
                )

            elif edge == 'edge_follow':
                """following"""
                self.following_set.add(user['node']['username'])
                yield InstagramFollowingItem(
                    user_id=user_data['id'],
                    user_name=user_data['username'],
                    following_id=user['node']['id'],
                    following_name=user['node']['username'],
                )

            else:
                pass

    def get_result_set(self, username):
        result_set = self.followers_set.intersection(self.following_set)
        if self.target_user in result_set:
            self.users_deque.clear()
            self.path.append(username)
            yield InstagramPathItem(start_user=self.start_user,
                                    target_user=self.target_user,
                                    path=self.path,
                                    )
        else:
            self.users_deque.extendleft(list(result_set))

            # yield InstagramUserItem(
            #     date_parse=datetime.now(),
            #     data=user['node'],
            # )
