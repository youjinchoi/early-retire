import os

from binance import Client
from dotenv import load_dotenv

from constants import Symbol
from results import PlaceOrderResult
from logger_factory import logger

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")


class BinanceService:
    def __init__(self):
        self._client = Client(API_KEY, API_SECRET)
        self._balance_dict = {Symbol.USDT: float(10000)}  # hardcode balance temporarily

    def get_price(self, pair_symbol) -> float:
        try:
            response = self._client.get_symbol_ticker(symbol=pair_symbol)
            price = float(response.get("price", 0))
            logger.debug(f"current {pair_symbol} price: {price}")
            return price
        except ConnectionError as error:
            logger.warning(f"binance price api error: {error}")
        except Exception:
            logger.exception("unexpected error while getting price from binance")

    def get_balance(self, symbol) -> float:
        return self._balance_dict[symbol, 0]

    def place_order(
        self,
        symbol_to_buy,
        symbol_to_sell,
        price: float,
        amount: float,
    ) -> PlaceOrderResult:
        required_balance = price * amount
        symbol_to_sell_balance = self._balance_dict.get(symbol_to_sell, float(0))
        if not symbol_to_sell_balance or symbol_to_sell_balance < required_balance:
            logger.error(
                f"insufficient {symbol_to_sell} balance: {symbol_to_sell_balance}"
            )
            return PlaceOrderResult(is_success=False)

        # call binance api later. assume all orders are hit
        new_symbol_to_sell_balance = symbol_to_sell_balance - required_balance
        self._balance_dict[symbol_to_sell] = symbol_to_sell_balance

        filled_balance = amount
        symbol_to_buy_balance = self._balance_dict.get(symbol_to_buy, float(0))
        new_symbol_to_buy_balance = symbol_to_buy_balance + filled_balance
        self._balance_dict[symbol_to_buy] = new_symbol_to_buy_balance

        return PlaceOrderResult(
            True,
            symbol_to_buy,
            new_symbol_to_buy_balance,
            symbol_to_sell,
            new_symbol_to_sell_balance,
        )
