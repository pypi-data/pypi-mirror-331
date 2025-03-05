from dataclasses import dataclass
from collections.abc import Sequence
from typing import Optional, Any

from steam_trader.exceptions import BadRequestError, Unauthorized, InternalError, UnknownItem, TooManyRequests
from ._base import TraderClientObject
from ._offers import SellOffer, BuyOffer
from ._misc import SellHistoryItem, Filters

@dataclass(slots=True)
class MinPrices(TraderClientObject):
    """Класс, представляющий минимальную/максимальную цену на предмет.

    Attributes:
        success (bool): Результат запроса.
        market_price (float, optional): Минимальная цена продажи. Может быть пустым.
        buy_price (float, optional): Максимальная цена покупки. Может быть пустым.
        steam_price (float, optional): Минимальная цена в Steam. Может быть пустым.
        count_sell_offers (int): Количество предложений о продаже.
        count_buy_offers (int): Количество предложений о покупке.
    """

    success: bool
    market_price: Optional[float]
    buy_price: Optional[float]
    steam_price: Optional[float]
    count_sell_offers: int
    count_buy_offers: int

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'MinPrices':

        if not data['success']:
            match data['code']:
                case 1:
                    raise InternalError('При выполнении запроса произошла неизвестная ошибка.')
                case 2:
                    raise UnknownItem('Неизвестный предмет.')

        data = super(MinPrices, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class ItemInfo(TraderClientObject):
    """Класс, представляющий информацию о группе предметов на сайте.

    Attributes:
        success (bool): Результат запроса.
        name (str): Локализованное (переведённое) название предмета.
        hash_name (str): Параметр 'market_hash_name' в Steam.
        type (str): Тип предмета (из Steam).
        gameid (int): AppID приложения в Steam.
        contextid (int): ContextID приложения в Steam.
        color (str): Hex код цвета предмета (из Steam).
        small_image (str): Абсолютная ссылка на маленькое изображение предмета.
        large_image (str): Абсолютная ссылка на большое изображение предмета.
        marketable (bool): Параметр 'marketable' в Steam.
        tradable (bool): Параметр 'tradable' в Steam.
        description (str): Локализованное (переведённое) описание предмета.
        market_price (float, optional): Минимальная цена продажи. Может быть пустым.
        buy_price (float, optional): Максимальная цена покупки. Может быть пустым.
        steam_price (float, optional): Минимальная цена в Steam. Может быть пустым.
        filters (steam_trader.Filters): Фильтры, используемые для поиска на сайте.
        sell_offers (Sequnce[steam_trader.SellOffer]): Последовательность с предложениями о продаже.
            От большего к меньшему.
        buy_offers (Sequnce[steam_trader.BuyOffer]): Последовательность с предложениями о покупке.
            От большего к меньшему.
        sell_history (Sequence[steam_trader.SellHistoryItem]): Последовательность истории продаж.
    """

    success: bool
    name: str
    hash_name: str
    type: str
    gameid: int
    contextid: int
    color: str
    small_image: str
    large_image: str
    marketable: bool
    tradable: bool
    description: str
    market_price: Optional[float]
    buy_price: Optional[float]
    steam_price: Optional[float]
    filters: Optional[Filters]
    sell_offers: Sequence[SellOffer]
    buy_offers: Sequence[BuyOffer]
    sell_history: Sequence[SellHistoryItem]

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'ItemInfo':

        if not data['success']:
            match data['code']:
                case 400:
                    raise BadRequestError('Неправильный запрос.')
                case 401:
                    raise Unauthorized('Неправильный api-токен.')
                case 429:
                    raise TooManyRequests('Вы отправили слишком много запросов.')
                case 1:
                    raise InternalError('При выполнении запроса произошла неизвестная ошибка.')
                case 2:
                    raise UnknownItem('Неизвестный предмет.')

        data['filters'] = Filters.de_json(data['filters'])

        for i, offer in enumerate(data['sell_offers']):
            data['sell_offers'][i] = SellOffer.de_json(offer)

        for i, offer in enumerate(data['buy_offers']):
            data['buy_offers'][i] = BuyOffer.de_json(offer)

        for i, item in enumerate(data['sell_history']):
            data['sell_history'][i] = SellHistoryItem.de_json(item)

        data = super(ItemInfo, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class OrderBook(TraderClientObject):
    """Класс, представляющий заявоки о покупке/продаже предмета.

    Attributes:
        success (bool): Результат запроса.
        sell (Sequence[Sequence[int]]): Сгруппированный по цене список заявок на продажу.
            Каждый элемент в списке является массивом, где первый элемент - это цена, а второй - количество заявок.
        buy (Sequence[Sequence[int]]): Сгруппированный по цене список заявок на покупку.
            Каждый элемент в списке является массивом, где первый элемент - это цена, а второй - количество заявок.
        total_sell (int): Количество всех заявок на продажу.
        total_buy (int): Количество всех заявок на покупку.
    """

    success: bool
    sell: Sequence[Sequence[int]]
    buy: Sequence[Sequence[int]]
    total_sell: int
    total_buy: int

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'OrderBook':

        if not data['success']:
            match data['code']:
                case 1:
                    raise InternalError('При выполнении запроса произошла ошибка.')

        data = super(OrderBook, cls)._de_json(data)

        return cls(**data)
