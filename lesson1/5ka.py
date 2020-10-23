import json
import requests


def save_to_json(category: dict):
    with open(f'category/{category["name"]}.json', 'w', encoding='UTF-8') as file:
        json.dump(category, file, ensure_ascii=False)


class CategoryParser5ka:
    __params = {
        'records_per_page': 50,
    }
    __headers = {
        'User_agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0',
    }

    def __init__(self, start_url, cat_url):
        self.start_url = start_url
        self.cat_url = cat_url

    def products_by_category(self, url_with_promo, category_code):
        params = self.__params
        params['categories'] = category_code
        result = []
        while url_with_promo:
            response = requests.get(url_with_promo, params=params, headers=self.__headers)
            data: dict = response.json()
            url_with_promo = data['next']
            result.extend(data['results'])
        return result

    def extract_category(self):
        response_cat = requests.get(self.cat_url, headers=self.__headers)
        categories: dict = response_cat.json()
        return categories

    def parse(self, url_to_parse=None, url_with_categories=None):
        if not url_to_parse:
            url_to_parse = self.start_url
        if not url_with_categories:
            categories = self.extract_category()
        else:
            self.cat_url = url_with_categories
            categories = self.extract_category()
        for category in categories:
            product_list = self.products_by_category(url_to_parse, category['parent_group_code'])
            result = {'name': category['parent_group_name'],
                      'code': category['parent_group_code'],
                      'products': product_list
                      }
            save_to_json(result)


if __name__ == '__main__':
    url = 'https://5ka.ru/api/v2/special_offers/'
    category_url = 'https://5ka.ru/api/v2/categories/'
    parser = CategoryParser5ka(url, category_url)
    parser.parse()

    print(1)
