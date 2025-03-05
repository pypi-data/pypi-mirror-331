######################################################################################
# ЭТО АВТОМАТИЧЕСКИ СОЗДАННАЯ КОПИЯ СИНХРОННОГО КЛИЕНТА. НЕ ИЗМЕНЯЙТЕ САМОСТОЯТЕЛЬНО #
######################################################################################

import httpx
import logging
from functools import wraps
from collections.abc import Sequence, Callable
from typing import Optional, Literal, Any, Self, TypeVar

from steam_trader.constants import SUPPORTED_APPIDS
from steam_trader.exceptions import *
from ._base import TraderClientObject
from ._account import WebSocketToken, Inventory, BuyOrders, Discounts, OperationsHistory, InventoryState, AltWebSocket
from ._buy import BuyResult, BuyOrderResult, MultiBuyResult
from ._sale import SellResult
from ._edit_item import EditPriceResult, DeleteItemResult, GetDownOrdersResult
from ._item_info import MinPrices, ItemInfo, OrderBook
from ._trade import ItemsForExchange, ExchangeResult, ExchangeP2PResult


logging.getLogger(__name__).addHandler(logging.NullHandler())

F = TypeVar('F', bound=Callable[..., Any])

def log(method: F) -> F:
    logger = logging.getLogger(method.__module__)

    @wraps(method)
    async def wrapper(*args, **kwargs):
        logger.debug(f'Entering: {method.__name__}')

        result = await method(*args, **kwargs)
        logger.info(result)

        logger.debug(f'Exiting: {method.__name__}')

        return result

    return wrapper  # type: ignore


class ClientAsync(TraderClientObject):
    """Класс, представляющий клиент Steam Trader.

    Args:
        api_token (str): Уникальный ключ для аутентификации.
        proxy (str, optional): Прокси для запросов. Для работы необходимо использовать контекстный менеджер with.
        base_url (str, optional): Ссылка на API Steam Trader.
        headers (dict, optional): Словарь, содержащий сведения об устройстве, с которого выполняются запросы.
            Используется при каждом запросе на сайт.
        **kwargs: Будут переданы httpx клиенту. Например timeout.

    Attributes:
        api_token (str): Уникальный ключ для аутентификации.
        proxy (str, optional): Прокси для запросов.
        base_url (str, optional): Ссылка на API Steam Trader.
        headers (dict, optional): Словарь, содержащий сведения об устройстве, с которого выполняются запросы.
            Используется при каждом запросе на сайт.
    
    Usage:

    ```python
    from steam_trader.api import Client

    client = Client('Ваш токен')
    ...

    # или

    with client:
        ...
    ```

    ```python
    from steam_trader.api import ClientAsync

    client = ClientAsync('Ваш токен')

    async def main():
        async with client:
            ...
    ```
    """

    __slots__ = [
        'proxy',
        'api_token',
        'base_url',
        'headers'
    ]

    def __init__(
            self,
            api_token: str,
            *,
            proxy: Optional[str] = None,
            base_url: Optional[str] = None,
            headers: Optional[dict] = None,
            **kwargs
    ) -> None:

        self.api_token = api_token

        if base_url is None:
            base_url = "https://api.steam-trader.com/"
        self.base_url = base_url

        if headers is None:
            headers = {
                'user-agent': 'python3',
                'wrapper': 'SteamTrader-Wrapper',
                'manufacturer': 'Lemon4ksan',
                'Api-Key': self.api_token
            }
        self.headers = headers

        self._httpx_client = None
        self._kwargs = kwargs
        self.proxy = proxy

    async def __aenter__(self) -> Self:
        self._httpx_client = httpx.AsyncClient(proxy=self.proxy, **self._kwargs)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._httpx_client:
            await self._httpx_client.aclose()

    async def _get_request(
        self,
        method: str,
        *,
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, Any]] = None,
        cookies: Optional[dict[str, str]] = None,
        **kwargs
    ) -> Any:
        """Создать GET запрос и вернуть данные.

        Args:
            method (str): API метод.
            headers (dict[str, str], optional): Заголовки запроса.
            params (dict[str, Any], optional): Параметры запроса.
            cookies (dict[str, str], optional): Куки запроса.
            **kwargs: Будут переданы httpx клиенту.

        Returns:
            Any: Ответ сервера.
        """
        if headers is None:
            headers = self.headers

        if not self._httpx_client:
            raise ClientError('Необходимо использовать контекст async with ClientAsync()')
        url: str = self.base_url + method
        result = await self._httpx_client.get(
            url,
            headers=headers,
            params=params,
            cookies=cookies,
            **kwargs
        )
        result = result.json()

        try:
            if not result['success']:
                match result['code']:
                    case 400:
                        raise BadRequestError('Неправильный запрос.')
                    case 401:
                        raise Unauthorized('Неправильный api-токен.')
                    case 429:
                        raise TooManyRequests('Вы отправили слишком много запросов.')
        except KeyError:
            pass
        
        return result
    
    async def _post_request(
        self,
        method: str,
        *,
        data: Optional[dict[str, Any]] = None
    ) -> Any:
        """Создать POST запрос, обработать базовые исключения и вернуть данные.

        Args:
            method (str): API метод.
            data (dict[str, Any], optional): Параметры для POST запроса.
        
        Raises:
            BadRequestError: Неправильный запрос.
            Unauthorized: Неправильный api-токен.
            TooManyRequests: Слишком много запросов.

        Returns:
            Any: Ответ сервера.
        """

        if not self._httpx_client:
            raise ClientError('Необходимо использовать контекст async with ClientAsync()')
        url: str = self.base_url + method
        if not self._httpx_client:
            raise ClientError('Необходимо использовать контекст async with ClientAsync()')
        result = (await self._httpx_client.post(
            url,
            headers=self.headers,
            data=data
        )).json()

        try:
            if not result['success']:
                match result['code']:
                    case 400:
                        raise BadRequestError('Неправильный запрос.')
                    case 401:
                        raise Unauthorized('Неправильный api-токен.')
                    case 429:
                        raise TooManyRequests('Вы отправили слишком много запросов.')
        except KeyError:
            pass
        
        return result
    
    @property
    async def balance(self) -> float:
        """Баланс клиента."""
        result = await self._get_request('getbalance/')
        return result['balance']

    @log
    async def sell(self, itemid: int, assetid: int, price: float) -> SellResult:
        """Создать предложение о продаже определённого предмета.

        Note:
            Если при создании предложения о ПРОДАЖЕ указать цену меньше, чем у имеющейся заявки на ПОКУПКУ,
            предложение о ПРОДАЖЕ будет исполнено моментально по цене заявки на ПОКУПКУ.
            Например, на сайте есть заявка на покупку за 10 ₽, а продавец собирается выставить предложение за 5 ₽
            (дешевле), то сделка совершится по цене 10 ₽.

        Args:
            itemid (int): Уникальный ID предмета.
            assetid (int): AssetID предмета в Steam (найти их можно через get_inventory).
            price (float): Цена, за которую хотите продать предмет без учёта комиссии/скидки.

        Returns:
            SellResult: Результат создания предложения о продаже.

        Raises:
            InternalError: При создании заявки произошла неизвестная ошибка.
            UnknownItem: Неизвестный предмет.
            NoTradeLink: Отсутствует сслыка для обмена.
            IncorrectPrice: Неправильная цена заявки.
            ItemAlreadySold: Предмет уже продан или отстутствует.
            AuthenticatorError: Мобильный аутентификатор не подключён
                или с момента его подключения ещё не прошло 7 дней.
        """
        result = await self._post_request('sale/', data={"itemid": itemid, "assetid": assetid, "price": price})
        return SellResult.de_json(result)

    @log
    async def buy(self, itemid: int | str, itemtype: Literal[1, 2, 3], price: float, currency: Literal[1] = 1) -> BuyResult:
        """Создать предложение о покупке предмета по строго указанной цене.

        Если в момент покупки цена предложения о продаже изменится, покупка не совершится.

        Note:
            Сайт пока работает только с рублями. Не меняйте значение currency.

        Args:
            itemid (int | str): В качества ID может выступать:
                GID для варианта покупки Commodity.
                Часть ссылки после nc/ (nc/L8RJI7XR96Mmo3Bu) для варианта покупки NoCommission.
                ID предложения о продаже для варианта покупки Offer (найти их можно в ItemInfo).
            itemtype (int): Вариант покупки (указаны выше) - 1 / 2 / 3.
            price (float): Цена предложения о продаже без учёта комиссии/скидки.
                Актуальные цены можно узнать через get_item_info и get_min_prices.
            currency (int): Валюта покупки. Значение 1 - рубль.

        Returns:
            BuyResult: Результат создания запроса о покупке.

        Raises:
            InternalError: При создании заявки произошла неизвестная ошибка.
            NoTradeLink: Отсутствует сслыка для обмена.
            NoLongerExists: Предложение больше недействительно.
            NotEnoughMoney: Недостаточно средств.
        """
        if itemtype not in range(1, 4):
            logging.warning(f"Неправильное значение _type '{itemtype}'")
        result = await self._post_request('buy/', data={"id": itemid, "type": itemtype, "price": price, "currency": currency})
        return BuyResult.de_json(result)

    @log
    async def create_buy_order(self, gid: int, price: float, *, count: int = 1) -> BuyOrderResult:
        """Создать заявку на покупку предмета с определённым GID.

        Note:
            Если при создании предложения о ПРОДАЖЕ указать цену меньше, чем у имеющейся заявки на ПОКУПКУ,
            предложение о ПРОДАЖЕ будет исполнено моментально по цене заявки на ПОКУПКУ.
            Например, на сайте есть заявка на покупку за 10 ₽, а продавец собирается выставить предложение за 5 ₽
            (дешевле), то сделка совершится по цене 10 ₽.

        Args:
            gid (int): ID группы предметов.
            price (float): Цена предмета, за которую будете его покупать без учёта комиссии/скидки.
            count (int): Количество заявок для размещения (не более 500). По умолчанию - 1.

        Returns:
            BuyOrderResult: Результат созданния заявки на покупку.

        Raises:
            InternalError: При создании заявки произошла неизвестная ошибка.
            UnknownItem: Неизвестный предмет.
            NoTradeLink: Отсутствует сслыка для обмена.
            NoLongerExists: Предложение больше недействительно.
            NotEnoughMoney: Недостаточно средств.
        """
        if not 1 <= count <= 500:
            logging.warning(f"Количество заявок должно быть от 1 до 500 (не '{count}')")
        result = await self._post_request('createbuyorder/', data={"gid": gid, "price": price, "count": count})
        return BuyOrderResult.de_json(result)

    @log
    async def multi_buy(self, gid: int, max_price: float, count: int) -> MultiBuyResult:
        """Создать запрос о покупке нескольких предметов с определённым GID.

        Будут куплены самые лучшие (дешёвые) предложения о продаже.

        Если максимальная цена ПОКУПКИ будет указана больше, чем у имеющихся предложений о ПРОДАЖЕ, ПОКУПКА
        совершится по цене предложений. Например, на сайте есть 2 предложения о продаже по цене 10 и 11 ₽,
        если при покупке указать максмальную цену 25 ₽, то сделки совершатся по цене 10 и 11 ₽,
        а общая сумма потраченных средств - 21 ₽.

        Если по указанной максимальной цене не окажется достаточно предложений о продаже,
        success будет равен False и будет указано кол-во оставшихся предметов по данной цене.

        Args:
            gid (int): ID группы предметов.
            max_price (float): Максимальная цена одного предмета без учета комиссии/скидки.
            count (int): Количество предметов для покупки.

        Returns:
            MultiBuyResult: Результат создания запроса на мульти-покупку.

        Raises:
            InternalError: При создании заявки произошла неизвестная ошибка.
            NoTradeLink: Отсутствует сслыка для обмена.
            NotEnoughMoney: Недостаточно средств.

        Changes:
            0.2.3: Теперь, если во время операции закончиться баланс, вместо ошибки,
                в датаклассе будет указано кол-во оставшихся предметов по данной цене.
        """
        result = await self._post_request('multibuy/', data={"gid": gid, "max_price": max_price, "count": count})
        return MultiBuyResult.de_json(result)

    @log
    async def edit_price(self, itemid: int, price: float) -> 'EditPriceResult':
        """Редактировать цену предмета/заявки на покупку.

        При редактировании может произойти моментальная продажа/покупка по аналогии тому,
        как это сделано в методах sell и create_buy_order.

        Args:
            itemid (int): ID предложения о продаже/заявки на покупку.
            price (float): Новая цена, за которую хотите продать/купить предмет без учёта комиссии/скидки.

        Returns:
            EditPriceResult: Результат запроса на изменение цены.

        Raises:
            InternalError: При выполнении запроса произошла неизвестная ошибка.
            UnknownItem: Предмет не был найден.
            IncorrectPrice: Неправильная цена заявки.
            NotEnoughMoney: Недостаточно средств.
        """
        result = await self._post_request('editprice/', data={"id": itemid, "price": price})
        return EditPriceResult.de_json(result)

    @log
    async def delete_item(self, itemid: int) -> DeleteItemResult:
        """Снять предмет с продажи/заявку на покупку.

        Args:
            itemid (int): ID продажи/заявки на покупку.

        Returns:
            DeleteItemResult: Результат запроса снятия предмета
                с продажи/заявки на покупку.

        Raises:
            InternalError: При выполнении запроса произошла неизвестная ошибка.
            UnknownItem: Неизвестный предмет.
        """
        result = await self._post_request('deleteitem/', data={"id": itemid})
        return DeleteItemResult.de_json(result)

    @log
    async def get_down_orders(self, gameid: int, *, order_type: Literal['sell', 'buy'] = 'sell') -> GetDownOrdersResult:
        """Снять все заявки на продажу/покупку предметов.

        Args:
            gameid (int): AppID приложения в Steam.
            order_type (str): Тип заявок для удаления:
                "sell" - предложения о ПРОДАЖЕ. Значение по умолчанию.
                "buy" - предложения о ПОКУПКЕ.

        Returns:
            GetDownOrdersResult: Результат снятия всех заявок
                на продажу/покупку предметов.

        Raises:
            InternalError: При выполнении запроса произошла неизвестная ошибка.
            NoTradeItems: Нет заявок на продажу/покупку.
            UnsupportedAppID: Указан недействительный gameid.
            ValueError: Указано недопустимое значение order_type.
        """
        if gameid not in SUPPORTED_APPIDS:
            raise UnsupportedAppID(f"Игра с AppID '{gameid}' в данный момент не поддерживается.")
        if order_type not in ['sell', 'buy']:
            logging.warning(f"Неизвестный тип '{order_type}'")

        result = await self._post_request('getdownorders/', data={"gameid": gameid, "type": order_type})
        return GetDownOrdersResult.de_json(result)

    @log
    async def get_items_for_exchange(self) -> ItemsForExchange:
        """Получить список предметов для обмена с ботом.

        Returns:
            ItemsForExchange: Cписок предметов для обмена с ботом.

        Raises:
            InternalError: При выполнении запроса произошла неизвестная ошибка.
            NoTradeItems: Нет предметов для обмена.
        """
        result = await self._get_request('itemsforexchange/')
        return ItemsForExchange.de_json(result)

    @log
    async def exchange(self) -> ExchangeResult:
        """Выполнить обмен с ботом.

        Note:
            Вы сами должны принять трейд в приложении Steam, у вас будет 3 часа на это.
            В противном случае трейд будет отменён.

        Returns:
            ExchangeResult: Результат обмена с ботом.

        Raises:
            InternalError: При выполнении запроса произошла неизвестная ошибка.
            NoTradeLink: Отсутствует сслыка для обмена.
            TradeCreationFail: Не удалось создать предложение обмена или бот не может отправить предложение обмена,
                так как обмены в Steam временно не работают, или ваш инвентарь переполнен, или у вас есть VAC бан.
            NoTradeItems: Нет предметов для обмена.
            ExpiredTradeLink: Ссылка для обмена больше недействительна.
            TradeBlockError: Steam Guard не подключён или стоит блокировка обменов.
            MissingRequiredItems: В инвентаре Steam отсутствуют необходимые для передачи предметы.
            HiddenInventory: Ваш инвентарь скрыт.
            AuthenticatorError: Мобильный аутентификатор не подключён,
                или с момента его подключения ещё не прошло 7 дней.
        """
        result = await self._get_request('exchange/')
        return ExchangeResult.de_json(result)

    @log
    async def get_items_for_exchange_p2p(self) -> ItemsForExchange:
        """Получить список предметов для p2p обмена.

        Returns:
            ItemsForExchange: Cписок предметов для p2p обмена.

        Raises:
            InternalError: При выполнении запроса произошла неизвестная ошибка.
            NoTradeItems: Нет предметов для обмена.
        """
        result = await self._get_request('itemsforexchangep2p/')
        return ItemsForExchange.de_json(result)

    @log
    async def exchange_p2p(self) -> ExchangeP2PResult:
        """Выполнить p2p обмен.

        Note:
            Вы сами должны передать предмет клиенту из полученной информации, у вас будет 40 минут на это.
            В противном случае, трейд будет отменён.

        Returns:
            ExchangeP2PResult: Результат p2p обмена.

        Raises:
            InternalError: При выполнении запроса произошла неизвестная ошибка.
            NoTradeLink: Отсутствует сслыка для обмена.
            TradeCreationFail: Не удалось создать предложение обмена или бот не может отправить предложение обмена,
                так как обмены в Steam временно не работают, или ваш инвентарь переполнен, или у вас есть VAC бан,
                или покупатель не указал свою ссылку для обмена.
            NoTradeItems: Нет предметов для обмена.
            NoSteamAPIKey: Отсутсвтвует ключ Steam API.
            AuthenticatorError: Мобильный аутентификатор не подключён,
                или с момента его подключения ещё не прошло 7 дней.
        """
        result = await self._get_request('exchange/')
        return ExchangeP2PResult.de_json(result)

    @log
    async def get_min_prices(self, gid: int, currency: Literal[1] = 1) -> MinPrices:
        """Получить минимальные/максимальные цены предмета.

        Note:
            Сайт пока работает только с рублями. Не меняйте значение currency.

        Args:
            gid (int): ID группы предметов.
            currency (int): Валюта, значение 1 - рубль.

        Returns:
            steam_trader.MinPrices: Минимальные/максимальные цены предмета.

        Raises:
            InternalError: При выполнении запроса произошла неизвестная ошибка.
            UnknownItem: Неизвестный предмет.
        """
        result = await self._get_request('getminprices/', params={"gid": gid, "currency": currency})
        return MinPrices.de_json(result)

    @log
    async def get_item_info(self, gid: int) -> ItemInfo:
        """Получить информацию о группе предметов.

        Args:
            gid (int): ID группы предметов.

        Returns:
            ItemInfo: Информация о группе предметов.

        Raises:
            InternalError: При выполнении запроса произошла неизвестная ошибка.
            UnknownItem: Неизвестный предмет.
        """
        result = await self._get_request('iteminfo/', params={"gid": gid})
        return ItemInfo.de_json(result)

    @log
    async def get_order_book(self, gid: int, *, mode: Literal['all', 'sell', 'buy'] = 'all', limit: Optional[int] = None) -> OrderBook:
        """Получить заявки о покупке/продаже предмета.

        Args:
            gid (int): ID группы предметов.
            mode (str): Режим отображения
                'all' - отображать покупки и продажи. Значение по умолчанию.
                'sell' - отображать только заявки на ПРОДАЖУ.
                'buy' - отображать только заявки на ПОКУПКУ.
            limit (int, optional): Максимальное количество строк в списке. По умолчанию - неограниченно

        Returns:
            OrderBook: Заявки о покупке/продаже предмета.

        Raises:
            InternalError: При выполнении запроса произошла неизвестная ошибка.
        """
        if mode not in ['all', 'sell', 'buy']:
            logging.warning(f"Неизвестный режим '{mode}'")

        result = await self._get_request('orderbook/', params={"gid": gid, "mode": mode, "limit": limit})
        return OrderBook.de_json(result)

    @log
    async def get_web_socket_token(self) -> WebSocketToken:
        """Получить токен для авторизации в WebSocket. Незадокументированно."""
        result = await self._get_request('getwstoken/', params={'key': self.api_token})
        return WebSocketToken.de_json(result)

    @log
    async def get_inventory(self, gameid: int, *, status: Optional[Sequence[Literal[0, 1, 2, 3, 4]]] = None) -> Inventory:
        """Получить инвентарь клиента, включая заявки на покупку и купленные предметы.

        По умолчанию возвращает список предметов из инвентаря Steam, которые НЕ выставлены на продажу.

        Args:
            gameid (int): AppID приложения в Steam.
            status (Sequence[int], optional):
                Указывается, чтобы получить список предметов с определенным статусом.

                Возможные статусы:
                0 - В продаже
                1 - Принять
                2 - Передать
                3 - Ожидается
                4 - Заявка на покупку

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

        result = await self._get_request('getinventory/', params=params)
        return Inventory.de_json(result, status)

    @log
    async def get_buy_orders(self, *, gameid: Optional[int] = None, gid: Optional[int] = None) -> BuyOrders:
        """Получить последовательность заявок на покупку. По умолчанию возвращаются заявки для всех
        предметов из всех разделов.

        При указании соответствующих параметров можно получить заявки из определённого раздела и/или предмета.

        Args:
            gameid (int, optional): AppID приложения в Steam.
            gid (int, optional): ID группы предметов.

        Returns:
            BuyOrders: Список заявок на покупку.

        Raises:
            UnsupportedAppID: Указан недействительный gameid.
            NoBuyOrders: Нет запросов на покупку.
        """
        if gameid is not None and gameid not in SUPPORTED_APPIDS:
            raise UnsupportedAppID(f'Игра с AppID {gameid}, в данный момент не поддерживается.')

        params = {}
        if gameid is not None:
            params['gameid'] = gameid
        if gid is not None:
            params['gid'] = gid

        result = await self._get_request('getbuyorders/', params=params)
        return BuyOrders.de_json(result)

    @log
    async def get_discounts(self) -> Discounts:
        """Получить комиссии/скидки и оборот на сайте.

        Данные хранятся в словаре data, где ключ - это AppID игры в Steam (См. steam_trader.constants).

        Returns:
            Discounts: Комиссии/скидки и оборот на сайте.
        """
        result = await self._get_request('getdiscounts/')
        return Discounts.de_json(result)

    @log
    async def set_trade_link(self, trade_link: str) -> None:
        """Установить ссылку для обмена.

        Args:
            trade_link (str): Ссылка для обмена,
                Например, https://steamcommunity.com/tradeoffer/new/?partner=453486961&token=ZhXMbDS9

        Raises:
            SaveFail: Не удалось сохранить ссылку обмена.
            WrongTradeLink: Указана ссылка для обмена от другого Steam аккаунта ИЛИ ссылка для обмена уже указана.
        """
        result = await self._post_request('settradelink/', data={"trade_link": trade_link})
        if not result['success']:
            try:
                match result['code']:
                    case 1:
                        raise SaveFail('Не удалось сохранить ссылку для обмена.')
            except KeyError:
                raise WrongTradeLink('Указана ссылка для обмена от другого Steam аккаунта ИЛИ ссылка для обмена уже указана.')

    @log
    async def remove_trade_link(self) -> None:
        """Удалить ссылку для обмена.

        Raises:
            SaveFail: Не удалось удалить ссылку обмена.
        """
        result = await self._post_request('removetradelink/', data={"trade_link": "1"})
        if not result['success']:
            match result['code']:
                case 1:
                    raise SaveFail('Не удалось удалить ссылку обмена.')

    @log
    async def get_operations_history(self, *, operation_type: Optional[Literal[1, 2, 3, 4, 5, 9, 10]] = None, page: int = 0) -> OperationsHistory:
        """Получить историю операций (По умолчанию все типы). В каждой странице до 100 пунктов.

        Args:
            operation_type (int, optional): Тип операции. Может быть пустым.
                1 - Покупка предмета
                2 - Продажа предмета
                3 - Возврат за покупку
                4 - Пополнение баланса
                5 - Вывести средства
                9 - Ожидание покупки
                10 - Штрафной балл
            page (int): Страница операций. Отсчёт начинается с 0.

        Returns:
            OperationsHistory: История операций.

        Changes:
            0.3.0: Добавлен аргумент page.
        """
        if operation_type is not None and operation_type not in (1, 2, 3, 4, 5, 9, 10):
            logging.warning(f"Неизвестный тип '{operation_type}'")
        result = await self._get_request('operationshistory/', params={"type": operation_type, "page": page})
        return OperationsHistory.de_json(result)

    @log
    async def update_inventory(self, gameid: int) -> None:
        """Обновить инвентарь игры на сайте.

        Args:
            gameid (int): AppID приложения в Steam.

        Raises:
            UnsupportedAppID: Указан недействительный gameid.
        """
        if gameid not in SUPPORTED_APPIDS:
            raise UnsupportedAppID(f'Игра с AppID {gameid}, в данный момент не поддерживается.')
        await self._get_request('updateinventory/', params={"gameid": gameid})

    @log
    async def get_inventory_state(self, gameid: int) -> InventoryState:
        """Получить текущий статус обновления инвентаря.

        Args:
            gameid (int): AppID приложения в Steam.

        Returns:
            InventoryState: Текущий статус обновления инвентаря.

        Raises:
            UnsupportedAppID: Указан недействительный gameid.
        """
        if gameid not in SUPPORTED_APPIDS:
            raise UnsupportedAppID(f'Игра с AppID {gameid}, в данный момент не поддерживается.')
        result = await self._get_request('inventorystate/', params={"gameid": gameid})
        return InventoryState.de_json(result)

    @log
    async def trigger_alt_web_socket(self) -> Optional[AltWebSocket]:
        """Создать запрос альтернативным WebSocket.
        Для поддержания активного соединения нужно делать этот запрос каждые 2 минуты.

        Возвращает None если новых сообщений нет. При этом соединение будет поддрежано.

        Returns:
            AltWebSocket, optional: Запрос альтернативным WebSocket.
        """
        result = await self._get_request('altws/')
        return AltWebSocket.de_json(result)
