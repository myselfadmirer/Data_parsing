from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gbscrapy import settings
from gbscrapy.spiders.youla import YoulaSpider
from gbscrapy.spiders.hh_remote import HhRemoteSpider

if __name__ == '__main__':
    """youla.ru"""
    # crawl_settings = Settings()
    # crawl_settings.setmodule(settings)
    # crawl_process = CrawlerProcess(settings=crawl_settings)
    # crawl_process.crawl(YoulaSpider)
    # crawl_process.start()

    """hh.ru"""
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)
    crawl_process = CrawlerProcess(settings=crawl_settings)
    crawl_process.crawl(HhRemoteSpider)
    crawl_process.start()
