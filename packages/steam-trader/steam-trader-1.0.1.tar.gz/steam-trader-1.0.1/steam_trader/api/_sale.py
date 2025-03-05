from dataclasses import dataclass
from typing import Optional, Any

from steam_trader import exceptions
from ._base import TraderClientObject

@dataclass(slots=True)
class SellResult(TraderClientObject):
    """Класс, представляющий информацию о выставленном на продажу предмете.

     Attributes:
        success (bool): Результат запроса.
        id: (int): ID продажи.
        position (int): Позиция предмета в очереди.
        fast_execute (bool): Был ли предмет продан моментально.
        nc (str): Идентификатор для бескомиссионной продажи предмета.
        price (float, optional): Цена, за которую был продан предмет с учетом комиссии.
            Указывается, если 'fast_execute' = True
        commission (float, optional): Размер комиссии в процентах, за которую был продан предмет.
            Указывается, если 'fast_execute' = True
     """

    success: bool
    id: int
    position: int
    fast_execute: bool
    nc: str
    price: Optional[float] = None
    commission: Optional[float] = None

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'SellResult':

        if not data['success']:
            match data['code']:
                case 1:
                    raise exceptions.InternalError('При создании запроса произошла неизвестная ошибка.')
                case 2:
                    raise exceptions.UnknownItem('Неизвестный предмет.')
                case 3:
                    raise exceptions.NoTradeLink('Отсутствует сслыка для обмена.')
                case 4:
                    raise exceptions.IncorrectPrice(data['error'])
                case 5:
                    raise exceptions.ItemAlreadySold('Предмет уже продан или отстутствует.')
                case 6:
                    raise exceptions.AuthenticatorError('Мобильный аутентификатор не подключён или с момента его подключения ещё не прошло 7 дней.')

        data = super(SellResult, cls)._de_json(data)

        return cls(**data)
