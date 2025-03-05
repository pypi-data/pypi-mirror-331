import logging
from dataclasses import dataclass
from collections.abc import Sequence
from typing import Optional, Any

from steam_trader.exceptions import BadRequestError, Unauthorized, NoBuyOrders, TooManyRequests
from ._base import TraderClientObject
from ._misc import InventoryItem, BuyOrder, Discount, OperationsHistoryItem, AltWebSocketMessage


@dataclass(slots=True)
class WebSocketToken(TraderClientObject):
    """Класс, представляющий WebSocket токен.

    Attributes:
        steam_id: (str): SteamID клиента.
        time: (int): Время создание токена.
        hash: (str): Хеш токена.
    """

    steam_id: str
    time: int
    hash: str

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'WebSocketToken':

        try:
            if not data['success']:
                match data['code']:
                    case 401:
                        raise Unauthorized('Вы не зарегистрированны.')
                    case 429:
                        raise TooManyRequests('Вы отправили слишком много запросов.')
        except KeyError:
            pass

        data = super(WebSocketToken, cls)._de_json(data)

        return cls(**data)


@dataclass(slots=True)
class Inventory(TraderClientObject):
    """Класс, представляющий инвентарь клиента.

    Attributes:
        success (bool): Результат запроса.
        count (int): Количество всех предметов в инвентаре Steam.
        gameid (int): AppID игры к которой принадлежит инвентарь.
        last_update (int): Timestamp последнего обновления инвентаря.
        items (Sequence[steam_trader.InventoryItem]): Последовательность с предметами в инвентаре.
    """

    success: bool
    count: int
    gameid: int
    last_update: int
    items: Sequence[InventoryItem]
    

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any],
            status: Optional[Sequence[int]] = None,
    ) -> 'Inventory':

        if not data['success']:
            try:
                match data['code']:
                    case 400:
                        raise BadRequestError('Неправильный запрос.')
                    case 401:
                        raise Unauthorized('Неправильный api-токен.')
                    case 429:
                        raise TooManyRequests('Вы отправили слишком много запросов.')
            except KeyError:
                del data['error']

        data.update({
            'gameid': data['game']
        })
        del data['game']

        if status is not None:
            new_data = []
            for i, offer in enumerate(data['items']):
                if offer['status'] in status:
                    new_data.append(InventoryItem.de_json(offer))

            data['items'] = new_data
        else:
            for i, offer in enumerate(data['items']):
                data['items'][i] = InventoryItem.de_json(offer)

        data = super(Inventory, cls)._de_json(data)

        return cls(**data)


@dataclass(slots=True)
class BuyOrders(TraderClientObject):
    """Класс, представляющий ваши запросы на покупку.

    Attributes:
        success (bool): Результат запроса.
        data (Sequence[steam_trader.BuyOrder]): Последовательность запросов на покупку.
    """

    success: bool
    data: Sequence[BuyOrder]
    

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'BuyOrders':

        if not data['success']:
            match data['code']:
                case 400:
                    raise BadRequestError('Неправильный запрос.')
                case 401:
                    raise Unauthorized('Неправильный api-токен.')
                case 429:
                    raise TooManyRequests('Вы отправили слишком много запросов.')
                case 1:
                    raise NoBuyOrders('Нет запросов на покупку.')

        for i, offer in enumerate(data['data']):
            data['data'][i] = BuyOrder.de_json(offer)

        data = super(BuyOrders, cls)._de_json(data)

        return cls(**data)


@dataclass(slots=True)
class Discounts(TraderClientObject):
    """Класс, представляющий комиссии/скидки на игры, доступные на сайте.

    Attributes:
        success (bool): Результат запроса.
        data (dict[int, steam_trader.Discount]): Словарь, содержащий комисии/скидки.
    """

    success: bool
    data: dict[int, Discount]
    

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'Discounts':

        if not data['success']:
            match data['code']:
                case 400:
                    raise BadRequestError('Неправильный запрос.')
                case 401:
                    raise Unauthorized('Неправильный api-токен.')
                case 429:
                    raise TooManyRequests('Вы отправили слишком много запросов.')

        # Конвертируем ключ в число для совместимости с константами
        data['data'] = {int(appid): Discount.de_json(_dict) for appid, _dict in data['data'].items()}
        data = super(Discounts, cls)._de_json(data)

        return cls(**data)


@dataclass(slots=True)
class OperationsHistory(TraderClientObject):
    """Класс, представляющий истории операций, произведённых на сайте.

    Attributes:
        success (bool): Результат запроса.
        data (Sequence[steam_trader.OperationsHistoryItem]): Последовательность историй операций.
    """

    success: bool
    data: Sequence[OperationsHistoryItem]
    

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'OperationsHistory':

        if not data['success']:
            match data['code']:
                case 400:
                    raise BadRequestError('Неправильный запрос.')
                case 401:
                    raise Unauthorized('Неправильный api-токен.')
                case 429:
                    raise TooManyRequests('Вы отправили слишком много запросов.')

        for i, item in enumerate(data['data']):
            data['data'][i] = OperationsHistoryItem.de_json(item)

        data = super(OperationsHistory, cls)._de_json(data)

        return cls(**data)


@dataclass(slots=True)
class InventoryState(TraderClientObject):
    """Класс, представляющий текущий статус инвентаря.

    Attributes:
        success (bool): Результат запроса.
        updating_now (bool): Инвентарь обновляется в данный момент.
        last_update (int): Timestamp, когда последний раз был обновлён инвентарь.
        items_in_cache (int): Количество предметов в инвентаре.
    """

    success: bool
    updating_now: bool
    last_update: int
    items_in_cache: int
    

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'InventoryState':

        data.update({  # перенос с camleCase на snake_case
            'updating_now': data['updatingNow'],
            'last_update': data['lastUpdate'],
            'items_in_cache': data['itemsInCache']
        })
        del data['updatingNow'], data['lastUpdate'], data['itemsInCache']

        data = super(InventoryState, cls)._de_json(data)

        return cls(**data)


@dataclass(slots=True)
class AltWebSocket(TraderClientObject):
    """Класс, представляющий запрос альтернативным WebSocket.

    Attributes:
        success (bool): Результат запроса. Если false, сообщений в поле messages не будет,
            при этом соединение будет поддержано.
        messages (Sequence[steam_trader.AltWebSocketMessage]): Последовательность с WebSocket сообщениями.
    """

    success: bool
    messages: Sequence[AltWebSocketMessage]
    

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> Optional['AltWebSocket']:

        if not data['success']:
            logging.debug('WebSocket соединение поддержано.')
            return

        for i, message in enumerate(data['messages']):
            data['messages'][i] = AltWebSocketMessage.de_json(message)

        data = super(AltWebSocket, cls)._de_json(data)

        return cls(**data)
