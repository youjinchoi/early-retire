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

    def _call_api(self, api: str, **kwargs):
        try:
            response = getattr(self._client, api)(**kwargs)
            logger.debug(response)
            return response
        except ConnectionError as error:
            logger.warning(f"binance {api} error: {error}")
        except Exception:
            logger.exception(f"unexpected binance {api} error")

    def fetch_coin_balance_in_wallet(self, symbols: list[str]) -> dict:
        response = self._call_api("get_all_coins_info")
        balance_dict = {}
        symbol_set = set(symbols)
        for item in response:
            coin = item.get("coin", None)
            if coin in symbol_set:
                balance_dict[coin] = {
                    "free": item["free"],
                    "locked": item["locked"],
                }
                logger.debug(item)

        return balance_dict

    def get_open_orders(self, pairs) -> dict:
        open_orders_dict = {}
        for pair in pairs:
            response = self._call_api("get_open_orders", symbol=pair)
            if response:
                for order in response:
                    orders = open_orders_dict.get(pair, [])
                    orders.append(order)
                open_orders_dict[pair] = orders
        return open_orders_dict

    def get_order(self, pair, order_id):
        response = self._call_api("get_order", symbol=pair, orderId=order_id)
        logger.debug(response)

    def get_price_change_statistics(self, pair: str):
        response = self._call_api("get_ticker", symbol=pair)
        if response:
            return {
                "high_price": response["highPrice"],
                "low_price": response["lowPrice"]
            }

    def get_price(self, pair_symbol) -> float:
        response = self._call_api("get_symbol_ticker", symbol=pair_symbol)
        price = float(response.get("price", 0))
        logger.debug(f"current {pair_symbol} price: {price}")
        return price

    def place_order(
        self,
        pair: str,
        trading_type: str,
        price: float,
        quantity: float,
    ) -> object:
        response = self._call_api(
            "create_test_order",
            symbol=pair,
            side=trading_type,
            type="LIMIT",
            timeInForce="GTC",
            price=price,
            quantity=quantity
        )
        logger.info(f"place order. {pair=}, {trading_type=}, {price=}, {quantity=}")
        return response

    def get_trade_fee(self, symbol: str):
        response = self._call_api("get_trade_fee", symbol=symbol)
        logger.debug(response)
