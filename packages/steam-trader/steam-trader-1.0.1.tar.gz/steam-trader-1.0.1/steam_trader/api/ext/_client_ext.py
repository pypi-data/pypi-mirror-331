import logging
from functools import wraps
from typing import Optional, Sequence, Callable, Any, Literal, cast

from ._misc import TradeMode, PriceRange

from steam_trader.constants import SUPPORTED_APPIDS
from steam_trader.exceptions import UnsupportedAppID, UnknownItem
from steam_trader.api import (
    Client,
    Filters,
    Inventory,
    SellResult
)


logging.getLogger(__name__).addHandler(logging.NullHandler())

def log(method: Callable[..., Any]) -> Any:
    logger = logging.getLogger(method.__module__)

    @wraps(method)
    def wrapper(*args, **kwargs) -> Any:
        logger.debug(f'Entering: {method.__name__}')

        result = method(*args, **kwargs)
        logger.info(result)

        logger.debug(f'Exiting: {method.__name__}')

        return result

    return wrapper



class ExtClient(Client):
    """Данный класс представляет расширенную версию обычного клиента.

    Args:
        api_token (str): Уникальный ключ для аутентификации.
        proxy (str, optional): Прокси для запросов. Для работы необходимо использовать контекстный менеджер with.
        base_url (str, optional): Ссылка на API Steam Trader.
        headers (dict, optional): Словарь, содержащий сведения об устройстве, с которого выполняются запросы.
            Используется при каждом запросе на сайт.

    Attributes:
        api_token (str): Уникальный ключ для аутентификации.
        proxy (str, optional): Прокси для запросов.
        base_url (str, optional): Ссылка на API Steam Trader.
        headers (dict, optional): Словарь, содержащий сведения об устройстве, с которого выполняются запросы.
            Используется при каждом запросе на сайт.

    Изменённые методы:
        get_inventory - Добавлена возможность указывать фильтр для отсеивания предметов
        (очень медленно на синхронном клиенте).

    Новые методы:
        multi_sell - Аналог multi_buy. В отличие от него, возвращает последовательноасть из результатов продаж, а не один объект.
        set_trade_mode - Позволяет задать режим торговли. Данного метода нет в документации.

    Raises:
        BadRequestError: Неправильный запрос.
        Unauthorized: Неправильный api-токен.
        TooManyRequests: Слишком много запросов.
    """

    def __init__(
            self,
            api_token: str,
            *,
            proxy: Optional[str] = None,
            base_url: Optional[str] = None,
            headers: Optional[dict] = None,
            **kwargs
    ) -> None:
        super().__init__(api_token, proxy=proxy, base_url=base_url, headers=headers, **kwargs)

    @log
    def get_inventory(
            self,
            gameid: int,
            *,
            filters: Optional[Filters] = None,
            status: Optional[Sequence[Literal[0, 1, 2, 3, 4]]] = None
    ) -> Inventory:
        """Получить инвентарь клиента, включая заявки на покупку и купленные предметы.

        EXT:
            Добавляен аргумент filters для отсеивания предметов.

        По умолчанию возвращает список предметов из инвентаря Steam, которые НЕ выставлены на продажу.

        Args:
            gameid (int): AppID приложения в Steam.
            filters (steam_trader.Filters, optional): Фильтр для отсеивания предметов.
            status (Sequence[int], optional):
                Указывается, чтобы получить список предметов с определенным статусом.

                Возможные статусы:
                0 - В продаже
                1 - Принять
                2 - Передать
                3 - Ожидается
                4 - Заявка на покупку

                Если не указавать, вернётся список предметов из инвентаря Steam, которые НЕ выставлены на продажу.

        Returns:
            Inventory: Инвентарь клиента, включая заявки на покупку и купленные предметы.

        Raises:
            UnsupportedAppID: Указан недействительный gameid.
            ValueError: Указан недопустимый статус.
        """

        if gameid not in SUPPORTED_APPIDS:
            raise UnsupportedAppID(f'Игра с AppID {gameid}, в данный момент не поддерживается.')
        params = {"gameid": gameid}

        if status is not None:
            for i, s in enumerate(status):
                if s not in range(5):
                    raise ValueError(f'Неизвестный статус {s}')
                params[f'status[{i}]'] = s

        result = self._get_request('getinventory/', params=params)
        inventory = Inventory.de_json(result, status)

        if filters is not None:
            logging.warning('Вы используете синхронный клиент. Запрос с фильтрами может занять до 2 минут. Если хотите ускорить время, используйте асинхронную версию.')
            new_items = []

            for item in inventory.items:
                item_filters = cast('Filters', self.get_item_info(item.gid).filters)
                if filters.quality is not None and item_filters.quality is not None:
                    required_filters_list = [_filter.id for _filter in filters.quality]
                    item_filters_list = [_filter.id for _filter in item_filters.quality]
                    if not any([required_filter in item_filters_list for required_filter in required_filters_list]):
                        continue
                if filters.type is not None and item_filters.type is not None:
                    required_filters_list = [_filter.id for _filter in filters.type]
                    item_filters_list = [_filter.id for _filter in item_filters.type]
                    if not any([required_filter in item_filters_list for required_filter in required_filters_list]):
                        continue
                if filters.used_by is not None and item_filters.used_by is not None:
                    required_filters_list = [_filter.id for _filter in filters.used_by]
                    item_filters_list = [_filter.id for _filter in item_filters.used_by]
                    if not any([required_filter in item_filters_list for required_filter in required_filters_list]):
                        continue
                if filters.craft is not None and item_filters.craft is not None:
                    required_filters_list = [_filter.id for _filter in filters.craft]
                    item_filters_list = [_filter.id for _filter in item_filters.craft]
                    if not any([required_filter in item_filters_list for required_filter in required_filters_list]):
                        continue
                if filters.region is not None and item_filters.region is not None:
                    required_filters_list = [_filter.id for _filter in filters.region]
                    item_filters_list = [_filter.id for _filter in item_filters.region]
                    if not any([required_filter in item_filters_list for required_filter in required_filters_list]):
                        continue
                if filters.genre is not None and item_filters.genre is not None:
                    required_filters_list = [_filter.id for _filter in filters.genre]
                    item_filters_list = [_filter.id for _filter in item_filters.genre]
                    if not any([required_filter in item_filters_list for required_filter in required_filters_list]):
                        continue
                if filters.mode is not None and item_filters.mode is not None:
                    required_filters_list = [_filter.id for _filter in filters.mode]
                    item_filters_list = [_filter.id for _filter in item_filters.mode]
                    if not any([required_filter in item_filters_list for required_filter in required_filters_list]):
                        continue
                if filters.trade is not None and item_filters.trade is not None:
                    required_filters_list = [_filter.id for _filter in filters.trade]
                    item_filters_list = [_filter.id for _filter in item_filters.trade]
                    if not any([required_filter in item_filters_list for required_filter in required_filters_list]):
                        continue
                if filters.rarity is not None and item_filters.rarity is not None:
                    required_filters_list = [_filter.id for _filter in filters.rarity]
                    item_filters_list = [_filter.id for _filter in item_filters.rarity]
                    if not any([required_filter in item_filters_list for required_filter in required_filters_list]):
                        continue
                if filters.hero is not None and item_filters.hero is not None:
                    required_filters_list = [_filter.id for _filter in filters.hero]
                    item_filters_list = [_filter.id for _filter in item_filters.hero]
                    if not any([required_filter in item_filters_list for required_filter in required_filters_list]):
                        continue

                new_items.append(item)

            inventory.items = new_items

        return inventory

    @log
    def multi_sell(self, gameid: int, gid: int, price: float, count: int) -> Sequence[SellResult]:
        """Продать множество вещей из инвенторя с одним gid.

        Args:
            gameid (int): AppID приложения в Steam.
            gid (int): ID группы предметов.
            price (float): Цена для выставления на продажу.
            count (int): Количество предметов для продажи. Если число больше чем предметов в инвенторе,
                будут проданы те, что имеются.

        Returns:
            Sequence[SellResult]: Последовательноасть с результатами продаж.

        Raises:
            OfferCreationFail: При создании заявки произошла неизвестная ошибка.
            UnknownItem: Неизвестный предмет.
            NoTradeLink: Отсутствует сслыка для обмена.
            IncorrectPrice: Неправильная цена заявки.
            ItemAlreadySold: Предмет уже продан или отстутствует.
            AuthenticatorError: Мобильный аутентификатор не подключён
                или с момента его подключения ещё не прошло 7 дней.
        """

        inventory = self.get_inventory(gameid)
        results = []

        for item in inventory.items:
            if count == 0:
                break
            if item.gid == gid:
                results.append(self.sell(item.itemid, item.assetid, price))
                count -= 1

        return results

    @log
    def set_trade_mode(self, state: Literal[0, 1]) -> TradeMode:
        """Задать режим торговли.

        Args:
            state (int): Режим торговли.
                0 - Торговля отключена.
                1 - Торговля включена.

        Returns:
            TradeMode: Режим торговли.

        Raises:
            ValueError: Недопустимое значение state.
        """

        if state not in range(2):
            raise ValueError(f'Недопустимое значение state :: {state}')

        result = self._get_request('startstoptrading/', params={"state": state})
        return TradeMode.de_json(result)

    @log
    def get_price_range(self, gid: int, *, mode: Literal['sell', 'buy', 'history'] = 'sell') -> PriceRange:
        """Получить размах цен.

        Args:
            gid (int): ID группы предметов.
            mode (str): Режим получения:
                'sell' - Цены запросов на продажу. Значение по умолчанию.
                'buy' - Цены запросов на покупку.
                'history' - Цены из истории продаж. Максимум 100 пунктов.

        Returns:
            PriceRange(lowest: float, highest: float): Размах цен в истории покупок.

        Raises:
            InternalError: При выполнении запроса произошла неизвестная ошибка.
            ValueError: Указано недопустимое значение mode.
            UnknownItem: Отсутствуют предложения о продаже/покупке или отсутствует история продаж.
        """

        lowest = highest = None

        match mode:
            case 'sell':
                sell_offers = self.get_order_book(gid)
                for item in sell_offers.sell:
                    if lowest is None or item[0] < lowest:
                        lowest = item[0]
                    if highest is None or item[0] > highest:
                        highest = item[0]
            case 'buy':
                buy_offers = self.get_order_book(gid)
                for item in buy_offers.buy:
                    if lowest is None or item[0] < lowest:
                        lowest = item[0]
                    if highest is None or item[0] > highest:
                        highest = item[0]
            case 'history':
                sell_history = self.get_item_info(gid)
                for item in sell_history.sell_history:
                    if lowest is None or item.price < lowest:
                        lowest = item.price
                    if highest is None or item.price > highest:
                        highest = item.price
        if lowest is None or highest is None:
            raise UnknownItem('Отсутствуют предложения о продаже/покупке или отсутствует история продаж.')
        return PriceRange(float(lowest), float(highest))
