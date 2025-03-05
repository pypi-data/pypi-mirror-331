import json
import bs4
from lxml import etree
from dataclasses import dataclass
from typing import Optional, cast
from collections.abc import Sequence
from ._base import WebClientObject
from steam_trader.exceptions import UnknownItem, NotFoundError


@dataclass(slots=True)
class MainPageItem(WebClientObject):
    """Класс, представляющий данные предмета на главной странице.

    Attributes:
        benefit (bool): True, если цена ниже чем в steam.
        count (int): Кол-во предложений.
        description (str): Описание первого предмета.
        gid (int): ID группы предметов.
        hash_name (str): Параметр hash_name в steam.
        image_small (str): Неабсолютная ссылка на маленькое изображение.
        name (str): Переведённое название предмета.
        outline (str): HEX код цвета названия.
        price (float): Цена самого дешёвого предложения.
        type (int): Тип/Уровень предмета.
    """

    benefit: bool
    count: int
    description: str
    gid: int
    hash_name: str
    image_small: str
    name: str
    outline: str
    price: float
    type: str

    @classmethod
    def de_json(cls, data: dict) -> 'MainPageItem':

        del data['color']
        data = super(MainPageItem, cls)._de_json(data)

        return cls(**data)


@dataclass(slots=True)
class MainPage(WebClientObject):
    """Класс, представляющий главную страничку продажи.

    Attributes:
        auth (bool): Истина если был указан правильный sessionid (sid).
        items (Sequence[MainPageItem]): Последовательность предметов.
        currency (int): Валюта. 1 - рубль.
        current_page (int): Текущая страница.
        page_count (int): Всего страниц.
        commission (int, optional): Коммиссия в %. Указывется если auth = True.
        discount (float): Скидка на покупки. Указывется если auth = True.
    """

    auth: bool
    items: Sequence['MainPageItem']
    currency: int
    current_page: int
    page_count: int
    commission: Optional[int] = None
    discount: Optional[float] = None

    @classmethod
    def de_json(cls, data: dict) -> 'MainPage':

        try:
            _ = data['error']
            raise NotFoundError('По данному запросу предметов не найдено.')
        except KeyError:
            pass

        try:
            data['items'] = data['contents']['items']
        except TypeError:
            data['items'] = []
        del data['contents']

        for i, item in enumerate(data['items']):
            data['items'][i] = MainPageItem.de_json(item)

        del data['body'], data['chat'], data['handler'], data['menu'], data['sorter'], data['title'], data['game']

        data = super(MainPage, cls)._de_json(data)

        return cls(**data)


@dataclass(slots=True)
class SellOffer(WebClientObject):
    """Класс, представляющий предложение о продаже.

    Attributes:
        id (int): Уникальный ID предложения.
        itemid (int): ID предмета.
        image_url (str): Неабсолютная ссылка на изображение предмета.
        name (str): Переведённое название предмета.
        type (int): Тип/Уровень предмета.
        price (float): Цена предложения.
    """

    id: int
    itemid: int
    image_url: str
    name: str
    type: str
    price: float

    @classmethod
    def de_json(cls, tag: bs4.Tag) -> 'SellOffer':

        tree = etree.HTML(str(tag))  # type: ignore
        _type = tree.xpath('//div/table/tr/td[2]/div[2]/p[2]')[0].text

        data = {
            'id': int(cast(str, tag.get('data-id'))),  # Названия одинаковые, но это ID предложения
            'itemid': int(tree.xpath('//div')[0].get('data-id')),  # А это ItemID
            'image_url': tree.xpath('//div/table/tr/td[1]/img')[0].get('src'),
            'name': tree.xpath('//div/table/tr/td[2]/div[1]')[0].text,
            'type': _type if _type is not None else '',
            # 'effect': tree.xpath('//div/table/tr/td[2]/div[3]')[0].text,  # Без понятия что это
            'price': float(tree.xpath('//div/table/tr/td[4]/div')[0].get('data-price').replace('\xa0', ''))
        }
        return cls(**data)


@dataclass(slots=True)
class ItemDescription(WebClientObject):
    """Класс, представляющйи данные предмета."""

    name: str
    type: str
    image_small: str
    color: str
    outline: str
    description: str

    @classmethod
    def de_json(cls, data: dict) -> 'ItemDescription':

        data = super(ItemDescription, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class ItemInfo(WebClientObject):
    """Класс, представляющий данные группы предметов.

    Attributes:
        auth (bool): Истина если был указан правильный sessionid (sid).
        sell_offers (Sequence[SellOffer): Последовательность предложений о продаже. Только для текущей страницы.
        descriptions (Sequence[dict[int, ItemDescription]]): Словарь с парами ItemID/описание.
            Только для текущей страницы. Если предмет типовой, равен None.
        item (bool): Истина если... если что?
        commission (int, optional): Коммиссия в %. Указывется если auth = True.
        discount (float): Скидка на покупки. Указывется если auth = True.
    """

    auth: bool
    sell_offers: Sequence['SellOffer']
    descriptions: Optional[dict[int, ItemDescription]]
    item: bool
    commission: Optional[int] = None
    discount: Optional[float] = None

    @classmethod
    def de_json(cls, data: dict) -> 'ItemInfo':

        html = bs4.BeautifulSoup(data['contents'], 'lxml')
        data['sell_offers'] = [SellOffer.de_json(tag) for tag in html.find_all('div', {'class': 'offer'})]

        try:
            script = cast(bs4.Tag, html.find('script')).text
            descriptions = dict(json.loads(script[script.index('var d=') + 6:script.index(';Market.setItemOffers(d,')]))
            for k, v in descriptions.copy().items():
                descriptions[int(k)] = ItemDescription.de_json(v)
                descriptions.pop(k)
        except ValueError:
            descriptions = None
        except AttributeError:
            raise UnknownItem('Неизвестный предмет.')

        data['descriptions'] = descriptions

        del data['title'], data['game'], data['menu'], data['contents']

        data = super(ItemInfo, cls)._de_json(data)

        return cls(**data)


@dataclass(slots=True)
class Referal(WebClientObject):
    """Класс, представляющий реферала.

    Attributes:
        name (str): Имя рефералла.
        date (str): Дата присоединения.
        status (str): Статус реферала.
        sum (float): Сумма потраченных рефералом средств.
    """

    name: str
    date: str
    status: str
    sum: float

    @classmethod
    def de_json(cls, data: dict) -> 'Referal':

        data = super(Referal, cls)._de_json(data)

        return cls(**data)


@dataclass(slots=True)
class HistoryItem(WebClientObject):
    """Класс, представляющий предмет из истории продаж.

    Attributes:
        name (str): Название предмета.
        date (str): Отформатированная строка времени.
        price (float): Цена, за которую был продан предмет.
        color (str): HEX код цвета текста названия.
        image_url (str): Неабсолютная ссылка на изображение предмета.
    """

    name: str
    date: str
    price: float
    color: str
    image_url: str

    @classmethod
    def de_json(cls, tag: bs4.Tag) -> 'HistoryItem':

        tree = etree.HTML(str(tag))  # type: ignore

        data = {
            'image_url': tree.xpath('//span[1]/img')[0].get('src'),
            'price': float(tree.xpath('//span[2]')[0].text.replace('\xa0', '').replace(',', '.')),
            'date': tree.xpath('//span[3]')[0].text,
            'name': tree.xpath('//span[4]')[0].text,
            'color': tree.xpath('//span[4]')[0].get('style')[7:]
        }
        return cls(**data)
