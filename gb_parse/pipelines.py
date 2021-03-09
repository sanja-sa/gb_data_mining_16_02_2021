# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo


class GbParsePipeline:
    def process_item(self, item, spider):
        return item


class GbParseMongoPipeline:
    _endpoint = "mongodb://localhost:27017"
    _db_name = "db_mining"
    _collection_name = "youla2"

    def __init__(self):
        self.collection = pymongo.MongoClient(self._endpoint)[self._db_name][self._collection_name]
        
    def process_item(self, item, spider):
        self.collection.insert_one(item)
        return item