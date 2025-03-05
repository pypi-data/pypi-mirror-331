from dataclasses import dataclass
from collections.abc import Sequence
from typing import Optional, Any

from ._base import TraderClientObject

@dataclass(slots=True)
class SellHistoryItem(TraderClientObject):
    """Класс, представляющий информацию о предмете в истории продаж.

    Attributes:
        date (int): Timestamp времени продажи.
        price (float): Цена предложения о покупке/продаже.
    """

    date: int
    price: float

    @classmethod
    def de_json(  # type: ignore
        cls,
        data: list
    ) -> 'SellHistoryItem':
        """Десериализация объекта.

        Args:
            data (dict): Поля и значения десериализуемого объекта.
            client (Union[steam_trader.Client, steam_trader.ClientAsync, None]):
                Клиент Steam Trader.

        Returns:
            steam_trader.SellHistoryItem: Информация о предмете в истории продаж.
        """

        return cls(
            date=data[0],
            price=float(data[1])
        )

@dataclass(slots=True)
class InventoryItem(TraderClientObject):
    """Класс, представляющий предмет в инвентаре.

    Attributes:
        id (int, optional): ID заявки на покупку/продажу. Может быть пустым.
        assetid (int, optional): AssetID предмета в Steam. Может быть пустым.
        gid (int): ID группы предметов.
        itemid (int): Уникальный ID предмета.
        price (float, optional): Цена, за которую предмет был выставлен/куплен/продан предмет без учёта
            скидки/комиссии. Может быть пустым.
        currency (int, optional): Валюта, за которую предмет был выставлен/куплен/продан. Значение 1 - рубль.
            Может быть пустым.
        timer (int, optional): Время, которое доступно для приема/передачи этого предмета. Может быть пустым.
        type (int, optional): Тип предмета. 0 - продажа, 1 - покупка. Может быть пустым.
        status (int): Статус предмета.
            -2 - Предмет в инвентаре Steam не выставлен на продажу.
            0 - Предмет выставлен на продажу или выставлена заявка на покупку. Для различия используется поле type.
            1 - Предмет был куплен/продан и ожидает передачи боту или P2P способом. Для различия используется поле type.
            2 - Предмет был передан боту или P2P способом и ожидает приёма покупателем.
            6 - Предмет находится в режиме резервного времени. На сайте отображается как "Проверяется"
                    после истечения времени на передачу боту или P2P способом.
        position (int, optional): Позиция предмета в списке заявок на покупку/продажу. Может быть пустым.
        nc (int, optional): ID заявки на продажу для бескомиссионной ссылки. Может быть пустым.
        percent (float, optional): Размер скидки/комиссии в процентах, с которой был куплен/продан предмет.
            Может быть пустым.
        steam_item (bool): Флаг, определяющий, имеется ли этот предмет в инвентаре в Steam (для продавца).
        nm (bool): Незадокументированно.
    """

    id: Optional[int]
    assetid: Optional[int]
    gid: int
    itemid: int
    price: Optional[float]
    currency: Optional[int]
    timer: Optional[int]
    type: Optional[int]
    status: int
    position: Optional[int]
    nc: Optional[int]
    percent: Optional[float]
    steam_item: bool
    nm: bool

    @classmethod
    def de_json(
        cls,
        data: dict[str, Any]
    ) -> 'InventoryItem':
        """Десериализация объекта.

        Args:
            data (dict): Поля и значения десериализуемого объекта.
            client (Union[steam_trader.Client, steam_trader.ClientAsync, None]):
                Клиент Steam Trader.

        Returns:
            steam_trader.InventoryItem: Предмет в инвентаре.
        """

        data = super(InventoryItem, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class Filter(TraderClientObject):
    """Класс, представляющий фильтр.

    Attributes:
        id (int, optional): ID фильтра, может быть пустым. Если вы создаёте класс вручную,
            то обязательно укажите этот параметр.
        title (str, optional): Тайтл фильтра, может быть пустым.
        color (str, optional): Hex цвет фильтра, может быть пустым.
    """

    id: Optional[int]
    title: Optional[str] = None
    color: Optional[str] = None

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'Filter':
        """Десериализация объекта.

        Args:
            data (dict): Поля и значения десериализуемого объекта.
            client (Union[steam_trader.Client, steam_trader.ClientAsync, None]):
                Клиент Steam Trader.

        Returns:
            steam_trader.Filter, optional: Фильтр.
        """

        data = super(Filter, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class Filters(TraderClientObject):
    """Класс, представляющий фильтры, используемые для поиска на сайте.

    Attributes:
        quality (Sequence[steam_trader.Filter], optional):
            Качество предмета (TF2, DOTA2).
        type (Sequence[steam_trader.Filter], optional):
            Тип предмета (TF2, DOTA2).
        used_by (Sequence[steam_trader.Filter], optional):
            Класс, который использует предмет (TF2).
        craft (Sequence[steam_trader.Filter], optional):
            Информация о карфте (TF2).
        region (Sequence[steam_trader.Filter], optional):
            Регион игры (SteamGift).
        genre (Sequence[steam_trader.Filter], optional):
            Жанр игры (SteamGift).
        mode (Sequence[steam_trader.Filter], optional):
            Тип игры, взаимодействие с Steam (SteamGift).
        trade (Sequence[steam_trader.Filter], optional):
            Информация об обмене (SteamGift).
        rarity (Sequence[steam_trader.Filter], optional):
            Редкость предмета (DOTA2).
        hero (Sequence[steam_trader.Filter], optional):
            Герой, который использует предмет (DOTA2).
    """

    quality: Optional[Sequence['Filter']] = None
    type: Optional[Sequence['Filter']] = None
    used_by: Optional[Sequence['Filter']] = None
    craft: Optional[Sequence['Filter']] = None
    region: Optional[Sequence['Filter']] = None
    genre: Optional[Sequence['Filter']] = None
    mode: Optional[Sequence['Filter']] = None
    trade: Optional[Sequence['Filter']] = None
    rarity: Optional[Sequence['Filter']] = None
    hero: Optional[Sequence['Filter']] = None

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'Filters':
        """Десериализация объекта.

        Args:
            data (dict): Поля и значения десериализуемого объекта.
            client (Union[steam_trader.Client, steam_trader.ClientAsync, None]):
                Клиент Steam Trader.

        Returns:
            steam_trader.Filters: Фильтры.
        """

        try:
            # TF2
            data.update({  # Затмевает встроенное имя class
                'used_by': data['class']
            })

            del data['class']

            for i, _filter in enumerate(data['quality']):
                data['quality'][i] = Filter.de_json(_filter)

            for i, _filter in enumerate(data['type']):
                data['type'][i] = Filter.de_json(_filter)

            for i, _filter in enumerate(data['used_by']):
                data['used_by'][i] = Filter.de_json(_filter)

            for i, _filter in enumerate(data['craft']):
                data['craft'][i] = Filter.de_json(_filter)

        except KeyError:
            try:
                # SteamGift
                for i, _filter in enumerate(data['region']):
                    data['region'][i] = Filter.de_json(_filter)

                for i, _filter in enumerate(data['genre']):
                    data['genre'][i] = Filter.de_json(_filter)

                for i, _filter in enumerate(data['mode']):
                    data['mode'][i] = Filter.de_json(_filter)

                for i, _filter in enumerate(data['trade']):
                    data['trade'][i] = Filter.de_json(_filter)

            except KeyError:
                # DOTA2
                for i, _filter in enumerate(data['rarity']):
                    data['rarity'][i] = Filter.de_json(_filter)

                for i, _filter in enumerate(data['quality']):
                    data['quality'][i] = Filter.de_json(_filter)

                for i, _filter in enumerate(data['type']):
                    data['type'][i] = Filter.de_json(_filter)

                for i, _filter in enumerate(data['hero']):
                    data['hero'][i] = Filter.de_json(_filter)

        data = super(Filters, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class BuyOrder(TraderClientObject):
    """Класс, представляющий информацию о запросе на покупку.

    Attributes:
        id (int): ID заявки на покупку.
        gid (int): ID группы предметов.
        gameid (int): AppID приложения в Steam.
        hash_name (str): Параметр market_hash_name в Steam.
        date (int): Timestamp подачи заявки.
        price (float): Предлагаемая цена покупки без учёта скидки.
        currency (int): Валюта, значение 1 - рубль.
        position (int): Позиция заявки в очереди.
    """

    id: int
    gid: int
    gameid: int
    hash_name: str
    date: int
    price: float
    currency: int
    position: int

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'BuyOrder':
        """Десериализация объекта.

        Args:
            data (dict): Поля и значения десериализуемого объекта.
            client (Union[steam_trader.Client, steam_trader.ClientAsync, None]):
                Клиент Steam Trader.

        Returns:
            steam_trader.BuyOrder: Информация о запрос на покупку.
        """

        data = super(BuyOrder, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class Discount(TraderClientObject):
    """Класс, представляющий информацию о комиссии/скидке в определённой игре.

    Attributes:
        total_buy (float): Cколько денег потрачено на покупки.
        total_sell (float): Cколько денег получено с продажи предметов.
        discount (float): Cкидка на покупку. Величина в %.
        commission (float): Комиссия на продажу. Величина в %.
    """

    total_buy: float
    total_sell: float
    discount: float
    commission: float

    @classmethod
    def de_json(
        cls,
        data: dict[str, Any]
    ) -> 'Discount':
        """Десериализация объекта.

        Args:
            data (dict): Поля и значения десериализуемого объекта.
            client (Union[steam_trader.Client, steam_trader.ClientAsync, None]):
                Клиент Steam Trader.

        Returns:
            steam_trader.Discount: Информацию о комиссии/скидке в определённой игре.
        """

        data = super(Discount, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class OperationsHistoryItem(TraderClientObject):
    """Класс, представляющий информацию о предмете в истории операций.

    Attributes:
        id (int): ID Операции.
        name (str): Название операции.
        type (int): Тип операции. 0 - продажа, 1 - покупка.
        amount (float): Сумма операции.
        currency (int): Валюта, значение 1 - рубль.
        date (int): Timestamp операции.
    """

    id: int
    name: str
    type: int
    amount: float
    currency: int
    date: int

    @classmethod
    def de_json(
        cls,
        data: dict[str, Any]
    ) -> 'OperationsHistoryItem':
        """Десериализация объекта.

        Args:
            data (dict): Поля и значения десериализуемого объекта.
            client (Union[steam_trader.Client, steam_trader.ClientAsync, None]):
                Клиент Steam Trader.

        Returns:
            steam_trader.OperationsHistoryItem: Информацию о предмете в истории операций.
        """

        data = super(OperationsHistoryItem, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class AltWebSocketMessage(TraderClientObject):
    """Класс, представляющий AltWebSocket сообщение.

    Attributes:
        type (int): Код WebSocket сообщения.
        data (str): WebSocket сообщение.
    """

    type: int
    data: str

    @classmethod
    def de_json(
        cls,
        data: dict[str, Any]
    ) -> 'AltWebSocketMessage':
        """Десериализация объекта.

        Args:
            data (dict): Поля и значения десериализуемого объекта.
            client (Union[steam_trader.Client, steam_trader.ClientAsync, None]):
                Клиент Steam Trader.

        Returns:
            steam_trader.AltWebSocketMessage: AltWebSocket сообщение.
        """

        data = super(AltWebSocketMessage, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class MultiBuyOrder(TraderClientObject):
    """Класс, представляющий предмет из запроса на мульти-покупку.

    Args:
        id (int): Уникальный ID заявки.
        itemid (int): ID предмета.
        price (float): Цена, за которую был куплен предмет с учётом скидки.
    """

    id: int
    itemid: int
    price: float

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'MultiBuyOrder':

        data = super(MultiBuyOrder, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class ItemForExchange(TraderClientObject):
    """Класс, представляющий информацию о предмете для передачи/получения боту.

    Attributes:
        id (int): ID покупки/продажи.
        assetid (int): AssetID предмета в Steam.
        gameid (int): AppID приложения в Steam.
        contextid (int): ContextID приложения в Steam.
        classid (int): Параметр ClassID в Steam.
        instanceid (int): Параметр InstanceID в Steam.
        gid (int): ID группы предметов.
        itemid (int): Уникальный ID предмета.
        price (float): Цена предмета, за которую купили/продали, без учета комиссии/скидки.
        currency (int): Валюта покупки/продажи.
        timer (int): Cколько времени осталось до передачи боту/окончания гарантии.
        asset_type (int): Значение 0 - этот предмет для передачи боту. Значение 1 - для приёма предмета от бота.
        percent (float): Размер комиссии/скидки в процентах, за которую был продан/куплен предмет.
        steam_item (bool): Присутствует ли предмет в вашем инвентаре Steam.
    """

    id: int
    assetid: int
    gameid: int
    contextid: int
    classid: int
    instanceid: int
    gid: int
    itemid: int
    price: float
    currency: int
    timer: int
    asset_type: int
    percent: float
    steam_item: bool

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'ItemForExchange':

        data = super(ItemForExchange, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class TradeDescription(TraderClientObject):
    """Класс, предстваляющий описание предмета для передачи/получения боту.

    Attributes:
        type (str): Тип предмета.
        description (str): Описание предмета.
        hash_name (str): Параметр market_hash_name в Steam.
        name (str): Локализованное (переведённое) название предмета.
        image_small (str): Маленькое изображение предмета.
        color (str): Цвет предмета (из Steam).
        outline (str): Цвет фильтра предмета (из Steam).
        gameid (int): AppID приложения в Steam
    """

    type: str
    description: str
    hash_name: str
    name: str
    image_small: str
    color: str
    outline: str
    gameid: int

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'TradeDescription':

        data = super(TradeDescription, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class ExchangeItem(TraderClientObject):
    """Класс, представляющий предмет, на который был отправлен обмен.

    Attributes:
        id (int): Уникальный ID заявки.
        assetid (int): AssetID предмета в Steam.
        gameid (int): AppID приложения в Steam.
        contextid (int): ContextID приложения в Steam.
        classid (int): ClassID предмета в Steam.
        instanceid (int): InstanceID предмета в Steam.
        type (int): Значение 0 - предмет для передачи боту, значение 1 - предмет для приема от бота.
        itemid (int): ID предмета.
        gid (int): Идентификатор группы предметов в нашей базе.
        price (int): Цена, за которую предмет был куплен/продан с учётом скидки/комиссии.
        currency (int): Валюта покупки/продажи.
        percent (float): Размер скидки/комиссии в процентах, с которой был куплен/продан предмет.
    """

    id: int
    assetid: int
    gameid: int
    contextid: int
    classid: int
    instanceid: int
    type: int
    itemid: int
    gid: int
    price: float
    currency: int
    percent: float

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'ExchangeItem':

        data = super(ExchangeItem, cls)._de_json(data)

        return cls(**data)
