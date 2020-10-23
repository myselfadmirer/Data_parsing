from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from pymongo import MongoClient
import dateparser


class MagnitParser:
    _headers = {
        'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:82.0) Gecko/20100101 Firefox/82.0",
    }
    _params = {
        'geo': 'istra',
    }

    def __init__(self, start_url):
        self.start_url = start_url
        self._url = urlparse(start_url)
        mongo_client = MongoClient('mongodb://localhost:27017')
        self.db = mongo_client['parse_istra_promo']

    def _get_soup(self, get_soup_url: str):
        params = self._params
        response = requests.get(get_soup_url, headers=self._headers, params=params)
        return BeautifulSoup(response.text, 'lxml')

    def parse(self):
        soup = self._get_soup(self.start_url)
        catalog = soup.find('div', attrs={'class': "сatalogue__main"})
        products = catalog.findChildren('a', attrs={'class': 'card-sale'})
        for product in products:
            if len(product.attrs.get('class')) > 2 or product.attrs.get('href')[0] != '/':
                continue
            product_url = f'{self._url.scheme}://{self._url.hostname}{product.attrs.get("href")}'
            product_soup = self._get_soup(product_url)
            product_data = self.get_product_structure(product_soup, product_url)
            self.save_to(product_data)

    def get_product_structure(self, product_soup, product_url):

        product = {'url': product_url, }

        product_template = {

            'promo_name': ('p', 'action__name-text', 'text'),
            'product_name': ('div', 'action__title', 'text'),
            'old_price': ('div', 'label__price_old', 'text'),
            'new_price': ('div', 'label__price_new', 'text'),
            'image_url': ('img', 'action__image', 'attrs'),
            'date_from': ('div', 'action__date-label', 'text'),
            'date_to': ('div', 'action__date-label', 'text'),
        }

        for key, value in product_template.items():
            try:
                product[key] = getattr(product_soup.find(value[0], attrs={'class': value[1]}), value[2])
            except Exception:
                product[key] = None
        try:
            product['image_url'] = f'{self._url.scheme}://{self._url.hostname}{product["image_url"]["data-src"]}'
        except Exception:
            product['image_url'] = None

        product = self.price(product, product_soup)
        product = self.dates(product)

        return product

    @staticmethod
    def price(product_dict: dict, product_soup):
        for key in ['old_price', 'new_price']:
            label = key[:3]
            try:
                product_dict[key] = getattr(product_soup.find('div', attrs={'class': 'action__price'}).find('div',
                                                                                                            attrs={
                                                                                                                'class': f'label__price_{label}'}),
                                            'text')
                product_dict[key] = product_dict[key].strip()
                product_dict[key] = product_dict[key].replace('\n', '.')
                product_dict[key] = float(product_dict[key])
            except Exception:
                product_dict[key] = None

        return product_dict

    @staticmethod
    def dates(product_dict: dict):
        promo_dates = product_dict['date_from']
        try:
            date_list = promo_dates.replace('с ', '').split(' по ')
        except Exception as e:
            date_list = [product_dict['date_from'], product_dict['date_to']]
        product_dict['date_from'] = dateparser.parse(date_list[0])
        product_dict['date_to'] = dateparser.parse(date_list[1])

        return product_dict

    def save_to(self, product_data: dict):
        collection = self.db['magnit']
        collection.insert_one(product_data)


if __name__ == '__main__':
    url = 'https://magnit.ru/promo/?geo='
    parser = MagnitParser(url)
    parser.parse()

    # Запрос для вывода товаров по группе:
    # db.magnit.find({promo_name: "Свежее предложение"})

    # Запрос для вывода групп товаров
    # db.magnit.distinct("promo_name")
