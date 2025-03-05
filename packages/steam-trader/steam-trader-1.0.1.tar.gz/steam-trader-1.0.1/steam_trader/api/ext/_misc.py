from dataclasses import dataclass
from typing import Any, Optional

from steam_trader.api import TraderClientObject
from steam_trader import exceptions

from collections import namedtuple
PriceRange = namedtuple('PriceRange', ['lowest', 'highest'])


@dataclass(slots=True)
class TradeMode(TraderClientObject):
    """Класс, представляющий режим торговли.

    Attributes:
        success (bool): Результат запроса.
        state (bool): Режим обычной торговли.
        p2p (bool): Режим p2p торговли.
    """

    success: bool
    state: Optional[bool] = None
    p2p: Optional[bool] = None

    @classmethod
    def de_json(
            cls,
            data: dict[str, Any]
    ) -> 'TradeMode':

        data = super(TradeMode, cls)._de_json(data)

        return cls(**data)

