import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gbscrapy import settings
from gbscrapy.spiders.youla import YoulaSpider
from gbscrapy.spiders.hh_remote import HhRemoteSpider
from gbscrapy.spiders.instagram import InstagramSpider
from dotenv import load_dotenv

load_dotenv('.env')

if __name__ == '__main__':
    """youla.ru"""
    # crawl_settings = Settings()
    # crawl_settings.setmodule(settings)
    # crawl_process = CrawlerProcess(settings=crawl_settings)
    # crawl_process.crawl(YoulaSpider)
    # crawl_process.start()

    # """hh.ru"""
    # crawl_settings = Settings()
    # crawl_settings.setmodule(settings)
    # crawl_process = CrawlerProcess(settings=crawl_settings)
    # crawl_process.crawl(HhRemoteSpider)
    # crawl_process.start()

    """www.instagram.com"""
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)
    crawl_process = CrawlerProcess(settings=crawl_settings)
    crawl_process.crawl(InstagramSpider, login=os.getenv('USERNAME'), enc_password=os.getenv('ENC_PASSWORD'))
    crawl_process.start()
