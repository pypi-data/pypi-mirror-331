import logging
from dataclasses import dataclass
from collections.abc import Sequence
from typing import Optional, Any

from .. import exceptions
from ._misc import MultiBuyOrder
from ._base import TraderClientObject

@dataclass(slots=True)
class BuyResult(TraderClientObject):
    """Класс, представляющий результат покупки.

    Attributes:
        success (bool): Результат запроса.
        id (int): Уникальный ID покупки.
        gid (int): ID группы предметов.
        itemid (int): ID купленного предмета.
        price (float): Цена, за которую был куплен предмет с учётом скидки.
        new_price (float): Новая цена лучшего предложения о продаже для варианта покупки Commodity,
            если у группы предметов ещё имеются предложения о продаже. Для остальных вариантов покупки будет 0
        discount (float): Размер скидки в процентах, за которую был куплен предмет.
    """

    success: bool
    id: int
    gid: int
    itemid: int
    price: float
    new_price: float
    discount: float

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'BuyResult':

        if not data['success']:
            match data['code']:
                case 1:
                    raise exceptions.InternalError('При создании запроса произошла неизвестная ошибка.')
                case 3:
                    raise exceptions.NoTradeLink('Отсутствует сслыка для обмена.')
                case 4:
                    raise exceptions.NoLongerExists('Предложение больше недействительно.')
                case 5:
                    raise exceptions.NotEnoughMoney('Недостаточно средств.')

        data = super(BuyResult, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class BuyOrderResult(TraderClientObject):
    """Класс, представляющий результат запроса на покупку.

    Attributes:
        success (bool): Результат запроса.
        executed (int): Количество исполненных заявок.
        placed (int): Количество размещённых на маркет заявок.
    """

    success: bool
    executed: int
    placed: int

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'BuyOrderResult':

        del data['orders']  # Конфликт с steam_trader.api.api.BuyOrder

        if not data['success']:
            match data['code']:
                case 1:
                    raise exceptions.InternalError('При создании запроса произошла неизвестная ошибка.')
                case 2:
                    raise exceptions.UnknownItem('Неизвестный предмет.')
                case 3:
                    raise exceptions.NoTradeLink('Отсутствует сслыка для обмена.')
                case 4:
                    raise exceptions.NoLongerExists('Предложение больше недействительно.')
                case 5:
                    raise exceptions.NotEnoughMoney('Недостаточно средств.')

        data = super(BuyOrderResult, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class MultiBuyResult(TraderClientObject):
    """Класс, представляющий результат мульти-покупки.

    Attributes:
        success (bool): Результат запроса.
        balance (float, optional): Баланс после покупки предметов. Указывается если success = True
        spent (float, optional): Сумма потраченных средств на покупку предметов. Указывается если success = True
        orders (Sequence[steam_trader.api.api.MultiBuyOrder], optional):
            Последовательность купленных предметов. Указывается если success = True
        left (int): Сколько предметов по этой цене осталось. Если операция прошла успешно, всегда равен 0.

    Changes:
        0.2.3: Теперь, если во время операции закончиться баланс, вместо ошибки,
            в датаклассе будет указано кол-во оставшихся предметов по данной цене.
    """

    success: bool
    balance: Optional[float] = None
    spent: Optional[float] = None
    orders: Optional[Sequence[MultiBuyOrder]] = None
    left: int = 0

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'MultiBuyResult':

        if not data['success']:
            match data['code']:
                case 1:
                    raise exceptions.InternalError('При создании запроса произошла неизвестная ошибка.')
                case 2:
                    logging.warning(data['error'])
                case 3:
                    raise exceptions.NoTradeLink('Отсутствует сслыка для обмена.')
                case 5:
                    raise exceptions.NotEnoughMoney('Недостаточно средств.')

        for i, offer in enumerate(data['orders']):
            data['orders'][i] = MultiBuyOrder.de_json(offer)

        data = super(MultiBuyResult, cls)._de_json(data)

        return cls(**data)
