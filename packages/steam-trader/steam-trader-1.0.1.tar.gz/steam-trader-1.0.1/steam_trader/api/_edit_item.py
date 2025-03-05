from dataclasses import dataclass
from collections.abc import Sequence
from typing import TYPE_CHECKING, Optional, Any

from steam_trader import exceptions
from ._base import TraderClientObject

if TYPE_CHECKING:
    from ._client import Client
    from ._client_async import ClientAsync

@dataclass(slots=True)
class EditPriceResult(TraderClientObject):
    """Класс, представляющий результат запроса на изменение цены.

    Attributes:
        success (bool): Результат запроса.
        type (int): Тип заявки. 0 - продажа, 1 - покупка.
        position (int): Позиция предмета в очереди.
        fast_execute (bool): Был ли предмет продан/куплен моментально.
        new_id (int, optional): Новый ID заявки. Указывается, если 'fast_execute' = true.
            Новый ID присваивается только заявкам на ПОКУПКУ и только в случае редактирования уже имеющейся заявки.
        price (float, optional): Цена, за которую был продан/куплен предмет с учётом комиссии/скидки.
            Указывается, если 'fast_execute' = true.
        percent (float, optional): Размер комиссии/скидки в процентах, за которую был продан/куплен предмет.
            Указывается, если 'fast_execute' = true.
    """

    success: bool
    type: int
    position: int
    fast_execute: bool
    new_id: Optional[int] = None
    price: Optional[float] = None
    percent: Optional[float] = None

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'EditPriceResult':

        if not data['success']:
            match data['code']:
                case 1:
                    raise exceptions.InternalError('При выполнении запроса произошла неизвестная ошибка.')
                case 2:
                    raise exceptions.UnknownItem('Предмет не был найден.')
                case 4:
                    raise exceptions.IncorrectPrice(data['error'])
                case 5:
                    raise exceptions.NotEnoughMoney('Для покупки не достаточно средств.')

        data = super(EditPriceResult, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class DeleteItemResult(TraderClientObject):
    """Класс, представляющий результат запроса снятия предмета с продажи/заявки на покупку.

    Attributes:
        success (bool): Результат запроса.
        has_ex (bool): Есть ли доступный обмен на сайте.
        has_bot_ex (bool): Есть ли доступный обмен с ботом.
        has_p2p_ex (bool): Есть ли доступный P2P обмен.
        total_fines (int): Общее количество штрафных баллов.
        fine_date (int, optional): Дата снятия штрафных баллов. Если None - штрафных баллов нет.
    """

    success: bool
    has_ex: bool
    has_bot_ex: bool
    has_p2p_ex: bool
    total_fines: int
    fine_date: Optional[int]

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'DeleteItemResult':

        if not data['success']:
            match data['code']:
                case 1:
                    raise exceptions.InternalError('При выполнении запроса произошла неизвестная ошибка.')
                case 2:
                    raise exceptions.UnknownItem('Неизвестный предмет.')

        data = super(DeleteItemResult, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class GetDownOrdersResult(TraderClientObject):
    """Класс, представляющий результат снятия всех заявок на продажу/покупку.

    Attributes:
        success (bool): Результат запроса.
        count (int): Количество удалённых предложений.
        ids (Sequence[int]): Список из ID удалённых предложений.
    """

    success: bool
    count: int
    ids: Sequence[int]

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'GetDownOrdersResult':

        if not data['success']:
            match data['code']:
                case 1:
                    raise exceptions.InternalError('При выполнении запроса произошла неизвестная ошибка.')
                case 2:
                    raise exceptions.NoTradeItems('Нет заявок на продажу/покупку.')

        data = super(GetDownOrdersResult, cls)._de_json(data)

        return cls(**data)
