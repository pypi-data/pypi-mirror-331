from dataclasses import dataclass
from collections.abc import Sequence
from typing import Any

from .. import exceptions
from ._base import TraderClientObject
from ._misc import TradeDescription, ItemForExchange, ExchangeItem
from ._p2p import P2PConfirmObject, P2PReceiveObject, P2PSendObject

@dataclass(slots=True)
class ItemsForExchange(TraderClientObject):
    """Класс, представляющий предметы для обмена с ботом.

    Attributes:
        success (bool): Результат запроса.
        items (Sequence[steam_trader.ItemForExchange]): Последовательность предметов для обмена с ботом.
        descriptions (dict[int, steam_trader.TradeDescription]): Описания предметов
            для обмена с ботом. Ключ - itemid предмета.
    """

    success: bool
    items: Sequence[ItemForExchange]
    descriptions: dict[int, TradeDescription]

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'ItemsForExchange':

        if not data['success']:
            match data['code']:
                case 1:
                    raise exceptions.InternalError('При выполнении запроса произошла неизвестная ошибка.')
                case 2:
                    raise exceptions.NoTradeItems('Нет предметов для обмена.')

        for i, item in enumerate(data['items']):
            data['items'][i] = ItemForExchange.de_json(item)

        # Конвертируем ключ в число
        data['descriptions'] = {
            int(_id): TradeDescription.de_json(_dict) for _id, _dict in data['descriptions'].items()
        }
        data = super(ItemsForExchange, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class ExchangeResult(TraderClientObject):
    """Класс, представляющий результат инициализации обмена с ботом.

    Attributes:
        success: (bool): Результат запроса.
        offer_id (int): ID обмена в Steam.
        code (str): Код проверки обмена.
        bot_steamid (int): SteamID бота, который отправил обмен.
        bot_nick (str): Ник бота.
        items (Sequence[steam_trader.ExchangeItem]): Cписок предметов для обмена с ботом.
    """

    success: bool
    offer_id: int
    code: str
    bot_steamid: int
    bot_nick: str
    items: Sequence[ExchangeItem]

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'ExchangeResult':

        if not data['success']:
            match data['code']:
                case 1:
                    raise exceptions.InternalError('При выполнении запроса произошла неизвестная ошибка.')
                case 2:
                    raise exceptions.NoTradeLink('Отсутствует сслыка для обмена.')
                case 3:
                    raise exceptions.TradeCreationFail('Не удалось создать предложение обмена. Повторите попытку позже.')
                case 4:
                    raise exceptions.NoTradeItems('Нет предметов для обмена.')
                case 5:
                    raise exceptions.ExpiredTradeLink('Ссылка для обмена больше недействительна.')
                case 6:
                    raise exceptions.TradeBlockError('Steam Guard не подключён или стоит блокировка обменов.')
                case 7:
                    raise exceptions.TradeCreationFail('Бот не может отправить предложение обмена, так как обмены в Steam временно не работают.')
                case 8:
                    raise exceptions.MissingRequiredItems('В инвентаре Steam отсутствуют необходимые для передачи предметы.')
                case 9:
                    raise exceptions.HiddenInventory('Ваш инвентарь скрыт.')
                case 10:
                    raise exceptions.TradeCreationFail('Бот не может отправить вам предложение обмена, потому что ваш инвентарь переполнен или у вас есть VAC бан.')
                case 11:
                    raise exceptions.AuthenticatorError('Мобильный аутентификатор не подключён, или с момента его подключения ещё не прошло 7 дней.')

        data.update({  # перенос с camleCase на snake_case
            'offer_id': data['offerId'],
            'bot_steamid': data['botSteamId'],
            'bot_nick': data['botNick']
        })
        del data['offerId'], data['botSteamId'], data['botNick']

        for i, item in enumerate(data['items']):
            data['items'][i] = ExchangeItem.de_json(item)

        data = super(ExchangeResult, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class ExchangeP2PResult(TraderClientObject):
    """Класс, представляющий результат инициализации p2p обмена.

    Attributes:
        success (bool): Результат запроса.
        send (Sequence[steam_trader.P2PSendObject]): Массив с данными для создания
            нового обмена в Steam.
        receive (Sequence[steam_trader.RecieveObject]): Массив с данными для принятия обмена.
        confirm (Sequence[steam_trader.ConfirmObject]): Массив с данными для подтверждения
            обмена в мобильном аутентификаторе.
        cancel (Sequence[str]): Массив из ID обменов, которые нужно отменить.
        client (Union[steam_trader.Client, steam_trader.ClientAsync, None]):
            Клиент Steam Trader.
    """

    success: bool
    send: Sequence[P2PSendObject]
    receive: Sequence[P2PReceiveObject]
    confirm: Sequence[P2PConfirmObject]
    cancel: Sequence[str]

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'ExchangeP2PResult':

        if not data['success']:
            match data['code']:
                case 1:
                    raise exceptions.InternalError('При выполнении запроса произошла неизвестная ошибка.')
                case 2:
                    raise exceptions.NoTradeLink('Отсутствует сслыка для обмена.')
                case 3:
                    raise exceptions.TradeCreationFail('Не удалось создать предложение обмена. Повторите попытку позже.')
                case 4:
                    raise exceptions.NoTradeItems('Нет предметов для обмена.')
                case 5:
                    raise exceptions.NoSteamAPIKey('Отсутсвтвует ключ Steam API.')
                case 6:
                    raise exceptions.TradeCreationFail('Невозможно создать обмен. Покупатель не указал свою ссылку для обмена.')
                case 7:
                    raise exceptions.AuthenticatorError('Мобильный аутентификатор не подключён, или с момента его подключения ещё не прошло 7 дней.')

        for i, item in enumerate(data['send']):
            data['send'][i] = P2PSendObject.de_json(item)

        for i, item in enumerate(data['receive']):
            data['receive'][i] = P2PReceiveObject.de_json(item)

        for i, item in enumerate(data['confirm']):
            data['confirm'][i] = P2PConfirmObject.de_json(item)

        data = super(ExchangeP2PResult, cls)._de_json(data)

        return cls(**data)
