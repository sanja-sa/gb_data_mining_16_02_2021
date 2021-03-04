from abc import abstractmethod


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
