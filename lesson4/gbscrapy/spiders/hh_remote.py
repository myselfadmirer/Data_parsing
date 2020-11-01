import scrapy
from ..loaders import HhRemoteLoaderVacancy, HhRemoteLoaderEmployer


class HhRemoteSpider(scrapy.Spider):
    name = 'hh_remote'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']
    xpath = {
        'vacancy': '//div[@class="vacancy-serp"]//span[@class="g-user-content"]/a/@href',
        'pagination': '//div[@data-qa="pager-block"]//a[@data-qa="pager-next"]/@href',
        'employers_vacancies': '//a[@data-qa="employer-page__employer-vacancies-link"]/@href',
    }
    vacancy_xpath = {
        'name': '//div[@class="vacancy-title"]/h1/text()',
        'salary': '//div[@class="vacancy-title"]/p[@class="vacancy-salary"]//text()',
        'description': '//div[@data-qa="vacancy-description"]//text()',
        'skills': '//div[@class="bloko-tag-list"]//span[@data-qa="bloko-tag__text"]/text()',
        'employer_url': '//a[@data-qa="vacancy-company-name"]/@href',
    }
    employer_xpath = {
        'name': '//div[@class="company-header"]//span[@data-qa="company-header-title-name"]/text()',
        'employer_url': '//div[@class="employer-sidebar-content"]/a[@class="g-user-content"]/@href',
        'areas_of_activity': '//div[@class="employer-sidebar-content"]//p/text()',
        'description': '//div[@data-qa="company-description-text"]/div[@class="g-user-content"]//text()',
    }

    def parse(self, response, **kwargs):
        """pagination"""
        for pag_url in response.xpath(self.xpath['pagination']):
            yield response.follow(pag_url, callback=self.parse)

        """vacancies"""
        for vac_url in response.xpath(self.xpath['vacancy']):
            yield response.follow(vac_url, callback=self.vacancy_parse)

    def vacancy_parse(self, response, **kwargs):
        """parameters of the vacancy"""
        loader = HhRemoteLoaderVacancy(response=response)
        loader.add_value('url', response.url)
        for key, value in self.vacancy_xpath.items():
            loader.add_xpath(key, value)

        yield loader.load_item()
        """employer's info"""

        employer_url = response.xpath(self.vacancy_xpath['employer_url'])
        for url in employer_url:
            yield response.follow(url, callback=self.employer_parse)

    def employer_parse(self, response, **kwargs):
        """employer"""
        loader = HhRemoteLoaderEmployer(response=response)
        loader.add_value('url', response.url)
        for key, value in self.employer_xpath.items():
            loader.add_xpath(key, value)

        yield loader.load_item()

        """all employer's vacancies"""
        for url in response.xpath(self.xpath['employers_vacancies']):
            yield response.follow(url, callback=self.parse)
