from dataclasses import dataclass
from typing import Any

from ._base import TraderClientObject

@dataclass(slots=True)
class SellOffer(TraderClientObject):
    """Класс, представляющий информацию о предложении продажи.

    Attributes:
        id (int): Уникальный ID заявки.
        classid (int): ClassID предмета в Steam.
        instanceid (int): InstanceID предмета в Steam.
        itemid (int): ID предмета.
        price (float): Цена предложения о покупке/продаже.
        currency (int): Валюта покупки/продажи.
    """

    id: int
    classid: int
    instanceid: int
    itemid: int
    price: float
    currency: int

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'SellOffer':

        data = super(SellOffer, cls)._de_json(data)

        return cls(**data)

@dataclass(slots=True)
class BuyOffer(TraderClientObject):
    """Класс, представляющий информацию о запросе на покупку.

    Attributes:
        id (int): ID заявки.
        price (float): Цена предложения о покупке/продаже.
        currency (int): Валюта покупки/продажи.
    """

    id: int
    price: float
    currency: int

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'BuyOffer':

        data = super(BuyOffer, cls)._de_json(data)

        return cls(**data)
