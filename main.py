"""
Источник https://auto.youla.ru/
Обойти все марки авто и зайти на странички объявлений
Собрать след структуру и сохранить в БД Монго
Название объявления
Список фото объявления (ссылки)
Список характеристик
Описание объявления
ссылка на автора объявления
дополнительно попробуйте вытащить телефона
"""


from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.autoyoula import AutoyoulaSpider


if __name__ == '__main__':
    crwl_settings = Settings()
    crwl_settings.setmodule("gb_parse.settings")
    crwl_proc = CrawlerProcess(settings=crwl_settings)
    crwl_proc.crawl(AutoyoulaSpider)
    crwl_proc.start()