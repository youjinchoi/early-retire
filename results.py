from dataclasses import dataclass
from typing import Optional


@dataclass
class PlaceOrderResult:
    is_success: bool
    symbol_to_buy: Optional[str]
    symbol_to_buy_balance: Optional[float]
    symbol_to_sell: Optional[str]
    symbol_to_sell_balance: Optional[float]


@dataclass
class Trade:
    pair: str
    trading_type: str
    price: float
    quantity: float
    profit_per_symbol: Optional[float]
