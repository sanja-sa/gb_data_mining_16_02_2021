import scrapy
import urllib.parse
from ..loaders import AutoyoulaLoader
from .autoyoula_cfg import XPATH
from base64 import b64decode
import json


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    def _get_follow(self, response, selector, cb, **kwargs):
        for link in response.xpath(XPATH[selector]):
            yield response.follow(link, callback=cb, cb_kwargs=kwargs)

    def car_parse(self, response, *args, **kwargs):
        loader = AutoyoulaLoader(response=response)
        loader.add_value("url", response.url)
        loader.add_xpath("characteristics", xpath=XPATH["article.chars"])
        loader.add_xpath("title", xpath=XPATH["article.title"])
        self._load_value_from_json(response, loader)
        yield loader.load_item()
     
    def brand_parse(self, response, *args, **kwargs):
        yield from self._get_follow(response, "next", self.brand_parse)
        yield from self._get_follow(response, "article", self.car_parse)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(response, "brands", self.brand_parse)

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

    def _load_value_from_json(self, response, loader):
        json_str_settings = response.xpath(XPATH["article.data"]["xpath"])\
                                .re_first(XPATH["article.data"]["regex"])

        list_settings = json.loads(urllib.parse.unquote(json_str_settings))
        settings = __class__._to_dict(list_settings)
        phones = settings["~#iM"]["advertCard"]["^0"]["contacts"]["^0"]["phones"]["^1"]
        images = settings["~#iM"]["advertCard"]["^0"]["media"]["^1"]
        loader.add_value("images", [ itm["^0"]["big"] for itm in images ])
        loader.add_value("phones", [ bytes.decode(b64decode(b64decode(itm["^0"]["phone"]))) for itm in phones ])
        loader.add_value("description", settings["~#iM"]["advertCard"]["^0"]["description"])

