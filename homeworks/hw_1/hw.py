import requests
import json
import time
import path


class Parser5ka:
    """
    Класс парсер 5-ки
    """
    def __init__(self, start_url:str, cat_url:str, products_path:path.Path):
        self.cat_url = cat_url
        self.start_url = start_url
        self.product_path = products_path        
   
    def run(self):
        #TODO: Предусмотреть механизм восстановления сканирования с определенной категории
        for category_code, category_name in self._parse_categories(self.cat_url):
            curr_product_idx = 0
            product_file = self.product_path.joinpath(f'{category_code}.json')
            product_file.write_text(f'{{\n"name":"{category_name}",\n"code":"{category_code}",\n"products":[')
            for product in self._parse(self.start_url, category_code):
                curr_product_idx += 1
                if curr_product_idx > 1:
                    product_file.write_text(f',\n', append=True)
                self._save(product, product_file)
            product_file.write_text(f']\n}}', append=True)

    @staticmethod            
    def _parse_categories(url:str):
        #TODO: Обработка ошибки структуры
        categories = __class__._get_response(url).json()
        for cat in categories:
            yield cat["parent_group_code"], cat["parent_group_name"]
        
    @staticmethod
    def _get_response(url:str, params:dict=None):
        while True:
            response = requests.get(url, params)
            if response.status_code == 200:
                return response
            time.sleep(0.5)

    @staticmethod
    def _parse(url:str, category:int):
        #TODO: Обработка ошибки структуры
        params = {'categories' : category}
        while url:
            data = __class__._get_response(url, params).json()
            url = data["next"]
            for product in data["results"]:
                yield product
        
    @staticmethod
    def _save(data:dict, file:str):
        jdata = json.dumps(data, ensure_ascii=False)
        file.write_text(jdata, append=True)


if __name__ == '__main__':
    api_url_5ka_categories = 'https://5ka.ru/api/v2/categories/'
    api_url_5ka = 'https://5ka.ru/api/v2/special_offers/'
    save_path = path.Path(__file__).parent.joinpath("products")
    if not save_path.exists():
        save_path.mkdir()
    parser = Parser5ka(api_url_5ka, api_url_5ka_categories, save_path)
    parser.run()