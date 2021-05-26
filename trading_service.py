import time

from binance_service import BinanceService
from constants import Symbol, Pair
from logger_factory import logger

TARGET_BUY_PRICE = 0.999
TARGET_SELL_PRICE = 1
TARGET_AMOUNT = 10000

DEFAULT_SLEEP_SECOND = 1


class TradingService:
    def __init__(self):
        self._symbol_to_buy = Symbol.BUSD
        self._symbol_to_sell = Symbol.USDT
        self._symbol_pair = Pair.BUSD_USDT
        self._total_coin_count = 10000
        self._binance_service = BinanceService()

    def _is_target_price(self, price: float) -> bool:
        if self._symbol_to_buy == Symbol.BUSD and price <= TARGET_BUY_PRICE:
            return True
        elif self._symbol_to_sell == Symbol.BUSD and price >= TARGET_SELL_PRICE:
            return True
        else:
            return False

    def _get_sleep_second(self, price: float) -> int:
        offset = 0
        if self._symbol_to_sell == Symbol.USDT:
            offset = price - TARGET_BUY_PRICE
        elif self._symbol_to_sell == Symbol.BUSD:
            offset = TARGET_SELL_PRICE - price

        return max(round(offset * 10000), DEFAULT_SLEEP_SECOND)

    def start(self):
        logger.info("start trading!")
        while True:
            price = self._binance_service.get_price(self._symbol_pair)
            if not price:
                logger.warning(f"invalid price for {self._symbol_pair}. {price=}")
                continue

            if not self._is_target_price(price):
                time.sleep(self._get_sleep_second(price))
                continue

            result = self._binance_service.place_order(
                self._symbol_to_buy, self._symbol_to_sell, price, float(TARGET_AMOUNT)
            )

            if not result.is_success:
                continue

            self._total_coin_count = (
                result.symbol_to_buy_balance + result.symbol_to_sell_balance
            )
            logger.info(
                f"order filled. now have {result.symbol_to_buy_balance} {result.symbol_to_buy} and {result.symbol_to_sell_balance} {result.symbol_to_sell}. total {self._total_coin_count} stable coins"
            )

            self._symbol_to_sell = result.symbol_to_buy
            self._symbol_to_buy = result.symbol_to_sell
            logger.info(
                f"waiting to buy {self._symbol_to_buy} and sell {self._symbol_to_sell}"
            )
