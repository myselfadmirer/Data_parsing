from urllib.parse import urlparse
import dateparser
import datetime
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from gbmodels import Base, Writer, Post, Tag, Comment, tag_post_table, comments_table


class GBParser:
    _params = {
        'commentable_id': 0
    }

    _headers = {
        'User_agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0',
    }

    def __init__(self, start_url, comments_url):
        self.session = SessionMaker()
        self.start_url = start_url
        self._url = urlparse(start_url)
        self.comments_url = comments_url

    def _get_soup(self, soup_url: str, param=None):
        if param:
            params = {
                'page': param
            }
            response = requests.get(soup_url, params=params, headers=self._headers)
        else:
            response = requests.get(soup_url, headers=self._headers)
        if response != '<Response [404]>':
            result = BeautifulSoup(response.text, 'lxml')
        else:
            result = 0

        return result

    def _get_tags(self, tag_soup, block, block_class):
        tag_soup = tag_soup.findChildren(block, attrs={'class': block_class})
        tags_dict = {}
        for tag in tag_soup:
            tag_url = f'{self._url.scheme}://{self._url.hostname}{tag.attrs.get("href")}'
            tag_name = getattr(tag, 'text')
            tags_dict[tag_name] = tag_url
        return tags_dict

    def _get_comments(self, p_id):
        params = {
            'commentable_id': p_id
        }
        post_comments = []
        comments_response = requests.get(self.comments_url, params=params, headers=self._headers)
        comments = comments_response.json()
        for comment in comments:
            while comment:
                comment = comment['comment']
                comment_dict = {'writer': comment['user']['full_name'],
                                'url': comment['user']['url'],
                                'text': comment['body']}
                post_comments.append(comment_dict)

                try:
                    comment = comment['children'][0]
                except IndexError:
                    comment = 0
        return post_comments

    def parse(self, url_to_parse=None):
        # data = []
        if not url_to_parse:
            url_to_parse = self.start_url
        count = 1
        soup = self._get_soup(url_to_parse, count)
        while soup:
            content = soup.find('div', attrs={'class': 'post-items-wrapper'})
            for child in content.children:
                post_url = child.findChild('a')
                post_url = f'{self._url.scheme}://{self._url.hostname}{post_url.attrs.get("href")}'
                post_attrs = {'url': post_url}

                post_soup = self._get_soup(post_url)
                post_soup = post_soup.find('article', attrs={'class': 'blogpost__article-wrapper'})

                post_date = post_soup.find('time').attrs.get('datetime')
                post_attrs['post_date'] = dateparser.parse(post_date)

                post_attrs['title'] = getattr(post_soup.find('h1', attrs={'class': 'blogpost-title'}), 'text')

                post_attrs['description'] = getattr(post_soup.find('div',
                                                                   attrs={'class': 'blogpost-description'}), 'text')

                post_attrs['post_img'] = post_soup.find('img').attrs.get('src')

                writer = post_soup.find('div', attrs={'class': 'col-md-5'})

                post_attrs['writer_name'] = getattr(writer.find('div', attrs={'itemprop': 'author'}), 'text')
                post_attrs['writer_url'] = f'{self._url.scheme}://{self._url.hostname}' \
                                           f'{writer.find("a").attrs.get("href")}'

                post_attrs['tags'] = self._get_tags(post_soup, 'a', 'small')

                post_id = post_soup.find('comments').attrs.get('commentable-id')
                comments_total = post_soup.find('comments').attrs.get('total-comments-count')
                comments_total = int(comments_total)
                if comments_total == 0:
                    post_attrs['comments'] = None
                else:
                    post_attrs['comments'] = self._get_comments(post_id)
                self.save_to_sqlite(post_attrs)
                # data.append(post_attrs)
            count += 1
            print(count)
            soup = self._get_soup(url_to_parse, count)
        self.session.commit()

    def save_to_sqlite(self, data: dict):
        writer = self.session.query(Writer).filter_by(url=data['writer_url']).first()
        if not writer:
            writer = Writer(name=data['writer_name'], url=data['writer_url'])
            self.session.add(writer)

        post = Post(url=data['url'], title=data['title'], description=data['description'], title_img=data['post_img'],
                    published_at=data['post_date'], writer_id=writer.id)
        self.session.add(post)

        tag_dict = data['tags']
        for key, value in tag_dict.items():
            tag = Tag(name=key, url=value)
            self.session.add(tag)
            tag_query = insert(tag_post_table).values(post_id=post.id, tag_id=tag.id)
            self.session.execute(tag_query)

        if data['comments']:
            for comment in data['comments']:
                comment_writer = self.session.query(Writer).filter_by(url=comment['url']).first()
                if not comment_writer:
                    comment_writer = Writer(name=comment['writer'], url=comment['url'])
                    self.session.add(comment_writer)
                comment = Comment(writer_id=comment_writer.id, text=comment['text'])
                self.session.add(comment)
                comment_query = insert(comments_table).values(post_id=post.id, comment_id=comment.id)
                self.session.execute(comment_query)


if __name__ == '__main__':

    engine = create_engine('sqlite:///gb_blog.db', echo=True)
    Base.metadata.create_all(bind=engine)

    SessionMaker = sessionmaker(bind=engine)

    url = 'https://geekbrains.ru/posts?page=1'
    comment_url = 'https://geekbrains.ru/api/v2/comments?commentable_type=Post&commentable_id=&order=desc'
    parser = GBParser(url, comment_url)
    parser.parse()
    print(1)
