from scrapy.loader import ItemLoader
from urllib.parse import urljoin
from scrapy import Selector
from itemloaders.processors import TakeFirst, MapCompose, Compose
from .items import GbAutoYoulaItem


def get_characteristics(item):
    selector = Selector(text=item)
    data = {
        "name": selector.xpath(
            "//div[contains(@class, 'AdvertSpecs_label')]/text()"
        ).extract_first(),
        "value": selector.xpath(
            "//div[contains(@class, 'AdvertSpecs_data')]//text()"
        ).extract_first(),
    }
    return data


def create_user_url(user_id):
    return urljoin("https://youla.ru/user/", user_id)


class AutoyoulaLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    characteristics_in = MapCompose(get_characteristics)
    user_url_in = MapCompose(create_user_url)
    user_url_out = TakeFirst()
    description_out = TakeFirst()
    phones_out = Compose()
    images_out = Compose()
