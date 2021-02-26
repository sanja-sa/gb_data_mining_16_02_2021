'''
Домашнее задание к уроку 2
https://magnit.ru/promo/?geo=moskva
Необходимо собрать структуры товаров по акции и сохранить их в MongoDB 
{
    "url": str,
    "promo_name": str,
    "product_name": str,
    "old_price": float,
    "new_price": float,
    "image_url": str,
    "date_from": "DATETIME",
    "date_to": "DATETIME",
}
'''


import requests
import json
import time
import re
from abc import abstractmethod
from urllib.parse import urljoin
from datetime import datetime
import path
from bs4 import BeautifulSoup as soup
import pymongo


class ProductStorage:
    """
    Базовый класс хранилища
    """
    def __init__(self):        
        pass

    @abstractmethod
    def save(self, product:dict):        
        '''
        Метод сохранения в хранилище
        '''
        pass

    @abstractmethod
    def dump(self):
        '''
        Метод вывода всех данных на экран в целях отладки
        '''
        pass

class ProductStorageMongoDB(ProductStorage):
    """
    Класс хранилища в MongoDB
    """
    def __init__(self, endpoint:str, db_name:str, collection_name:str):
        self.collection = pymongo.MongoClient(endpoint)[db_name][collection_name]
        
    def save(self, product:dict):        
        '''
        Метод сохранения в хранилище БД MongoDB
        '''
        self.collection.insert_one(product)

    def dump(self):
        '''
        Метод вывода всех данных на экран в целях отладки
        '''
        for itm in self.collection.find():
            print(itm)
        
class ParserMagnit:
    """
    Класс парсер магнита
    """

    month_indexes = {"янв":1, "фев":2, "мар":3, "апр":4, "мая":5, "июн":6, "июл":7, "авг":8, "сен":9, "окт":10, "ноя":11, "дек":12}

    def __init__(self, start_url:str, storage):
        self.start_url = start_url
        self.storage = storage
   
    def run(self):
        for product in self._parse(self.start_url):
            self.storage.save(product)
        
    @staticmethod
    def _get_response(url:str, params:dict=None):
        while True:
            response = requests.get(url, params)
            if response.status_code == 200:
                return response.content
            time.sleep(0.5)

    @staticmethod
    def _parse(url:str):
        
        year = datetime.now().year
        def parse_product_block(product)->dict:

            def get_price(div_block_price):
                try:  return float(div_block_price.span.get_text()) + float(div_block_price.span.findNextSibling().get_text())/100 
                except: return None

            def get_datetime(text:str)->datetime:
                try:
                    #TODO: Оптимизировать и вручную распарсить строку
                    day_month = re.match("^\w+\s(\d{1,2})\s+(\w{3})", text).groups()
                    return datetime(year, __class__.month_indexes[day_month[1].lower()], int(day_month[0]))
                except: 
                    return None

            try:
                promo_block = product.find("div", {"class": "card-sale__header"}, recursive=False)
                image_block = product.find("div", {"class": "card-sale__col card-sale__col_img"}, recursive=False)
                price_block = image_block.find("div", {"class":"label label_magnit card-sale__price"}, recursive=False)
                content_block = product.find("div", {"class": "card-sale__col card-sale__col_content"}, recursive=False)
                date_block = content_block.find("div", {"class": "card-sale__footer"}, recursive=False)
                return {
                    'url': urljoin(url, product["href"]),
                    'promo_name': promo_block.p.text,
                    'image_url': urljoin(url, image_block.img["data-src"]),
                    'product_name': image_block.img["alt"],
                    'new_price': get_price(price_block.find("div", {"class":"label__price label__price_new"}, recursive=False)) if price_block is not None else None,
                    'old_price': get_price(price_block.find("div", {"class":"label__price label__price_old"}, recursive=False)) if price_block is not None else None,
                    'date_from': get_datetime(date_block.div.p.text),
                    'date_to': get_datetime(date_block.div.p.findNextSibling().text),
                }
            except:
                #TODO: Сообщение об ошибке
                return None

        raw_content = __class__._get_response(url)
        structured_content = soup(raw_content, "lxml")
        product = structured_content.find("a", {"class": "card-sale card-sale_catalogue"})
        while product:
            product_data = parse_product_block(product)
            if product_data:
                yield product_data
            product = product.findNextSibling()
            
if __name__ == '__main__':
    start_url = 'https://magnit.ru/promo/?geo=moskva'
    try:
        storage = ProductStorageMongoDB("mongodb://localhost:27017", "db_mining", "magnit")
        parser = ParserMagnit(start_url, storage)
    except:
        #TODO: Сообщение об ошибке инициализации
        exit
    parser.run()
    storage.dump()
