from base_storage import ProductStorage
import pymongo


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
        