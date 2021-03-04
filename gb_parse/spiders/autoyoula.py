import scrapy
import urllib.parse
import json
from base64 import b64decode

class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']
    _css_selectors = {
        'brands' :  "div.TransportMainFilters_brandsList__2tIkv "
                    ".ColumnItemList_item__32nYI "
                    "a.blackLink",

        "next" :    "div.Paginator_block__2XAPy "
                    "a.Paginator_button__u1e7D",

        "article" : "article.SerpSnippet_snippet__3O1t2 "
                    ".SerpSnippet_titleWrapper__38bZM "
                    "a.blackLink",

        "article.title": "div.AdvertCard_advertTitle__1S1Ak::text",
        "article.chars.titles": "div.AdvertSpecs_label__2JHnS::text",
        "article.chars.values": "div.AdvertSpecs_data__xK2Qx ::text",
    }

    def __init__(self, *args, **kwargs):
        self.storage = kwargs['storage'] if 'storage' in kwargs else None
        
    def _get_follow(self, response, selector, cb, **kwargs):
        for link in response.css(self._css_selectors[selector]):
            url = link.attrib.get("href")
            yield response.follow(url, callback=cb, cb_kwargs=kwargs)

    @staticmethod
    def _to_dict(settings):
        def list_to_dict(itm):
            return {itm[i]: itm[i + 1] for i in range(0, len(itm), 2)} if (type(itm) == list and len(itm) > 1 and type(itm[0]) == str) else itm
        settings = list_to_dict(settings)
        if type(settings) == dict:
            for key in settings: 
                settings[key] = __class__._to_dict(settings[key])
        elif type(settings) == list:
            for idx, itm in enumerate(settings): 
                settings[idx] = __class__._to_dict(itm)
        return settings

    def car_parse(self, response, *args, **kwargs):

        def get_car_data():
            char_titles = response.css(self._css_selectors["article.chars.titles"]).extract()
            chars = response.css(self._css_selectors["article.chars.values"]).extract()
            json_str_settings = response.css("script::text").re_first('^window\.transitState\s*=\s*decodeURIComponent\(\\"(...+)\\"\)\;')
            list_settings = json.loads(urllib.parse.unquote(json_str_settings))
            settings = __class__._to_dict(list_settings)
            # TODO: Оптимизнуть и сделать строку путь в настройках
            phones = settings["~#iM"]["advertCard"]["^0"]["contacts"]["^0"]["phones"]["^1"]
            images = settings["~#iM"]["advertCard"]["^0"]["media"]["^1"]
            return {
                "_id": settings["~#iM"]["advertCard"]["^0"]["id"],
                "title" : response.css(self._css_selectors["article.title"]).extract_first(),
                "characteristics" : dict(zip(char_titles, chars)),
                "phones" : [ bytes.decode(b64decode(b64decode(itm["^0"]["phone"]))) for itm in phones ],
                "images" : [ itm["^0"]["big"] for itm in images ],
                "description" : settings["~#iM"]["advertCard"]["^0"]["description"],
                "user_url" : f'https://youla.ru/user/{settings["~#iM"]["advertCard"]["^0"]["youlaProfile"]["^0"]["youlaId"]}',
            }

        # Выделим требуху, если получиться
        try:
            self.storage.save(get_car_data())
        except:
            # TODO: Криво структуру смотрим
            print("Проверить структуру для парсинга")
     
    def brand_parse(self, response, *args, **kwargs):
        yield from self._get_follow(response, "next", self.brand_parse)
        yield from self._get_follow(response, "article", self.car_parse)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(response, "brands", self.brand_parse)
