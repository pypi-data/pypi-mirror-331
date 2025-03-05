from dataclasses import dataclass
from collections.abc import Sequence
from typing import Any

from ._base import TraderClientObject
from ._misc import ExchangeItem

@dataclass(slots=True)
class P2PTradeOffer(TraderClientObject):
    """Класс, представляющий данные для совершения p2p трейда. Незадокументированно.

    Attributes:
        sessionid (`str`):
        serverid (`int`):
        partner (`str`):
        tradeoffermessage (`str`):
        json_tradeoffer (`str`):
        captcha (`str`):
        trade_offer_create_params (`str`):
    """

    sessionid: str
    serverid: int
    partner: str
    tradeoffermessage: str
    json_tradeoffer: str
    captcha: str
    trade_offer_create_params: str

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'P2PTradeOffer':

        data = super(P2PTradeOffer, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class P2PSendObject(TraderClientObject):
    """Класс, представляющий ссылку на p2p обмен и сам обмен.

    Attributes:
        trade_link (`str`): Ссылка для p2p обмена.
        trade_offer (`steam_trader.P2PTradeOffer`): Параметры для POST запроса
            (https://steamcommunity.com/tradeoffer/new/send) при создании обмена в Steam. Вместо {sessionid} нужно
            указывать ID своей сессии в Steam.
    """

    trade_link: str
    trade_offer: P2PTradeOffer

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'P2PSendObject':

        data.update({  # перенос с camleCase на snake_case
            'trade_link': data['tradeLink'],
            'trade_offer': data['tradeOffer']
        })
        del data['tradeLink'], data['tradeOffer']

        data['trade_offer'] = P2PTradeOffer.de_json(data['trade_offer'])

        data = super(P2PSendObject, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class P2PReceiveObject(TraderClientObject):
    """Класс, представляющий массив с данными для принятия обмена.

    Attributes:
        offerid (`int`): ID обмена в Steam.
        code (`str`): Код проверки обмена.
        items (Sequence[`steam_trader.ExchangeItem`]): Список предметов в обмене.
        partner_steamid (`int`): SteamID покупателя.
    """

    offerid: int
    code: str
    items: Sequence[ExchangeItem]
    partner_steamid: int

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'P2PReceiveObject':

        data.update({  # перенос с camleCase на snake_case
            'offerid': data['offerId'],
            'partner_steamid': data['partnerSteamId']
        })
        del data['offerId'], data['partnerSteamId']

        for i, item in enumerate(data['items']):
            data['items'][i] = ExchangeItem.de_json(item)

        data = super(P2PReceiveObject, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class P2PConfirmObject(TraderClientObject):
    """Класс, представляющий массив с данными для подтверждения обмена в мобильном аутентификаторе.

    Attributes:
        offerid (`int`): ID обмена в Steam
        code (`str`): Код проверки обмена
        partner_steamid (`int`) SteamID покупателя
    """

    offerid: int
    code: str
    partner_steamid: int

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'P2PConfirmObject':

        data.update({  # перенос с camleCase на snake_case
            'offerid': data['offerId'],
            'partner_steamid': data['partnerSteamId']
        })
        del data['offerId'], data['partnerSteamId']

        data = super(P2PConfirmObject, cls)._de_json(data)

        return cls(**data)
