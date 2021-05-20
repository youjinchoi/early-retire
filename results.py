from dataclasses import dataclass
from typing import Optional


@dataclass
class PlaceOrderResult:
    is_success: bool
    symbol_to_buy: Optional[str]
    symbol_to_buy_balance: Optional[float]
    symbol_to_sell: Optional[str]
    symbol_to_sell_balance: Optional[float]
