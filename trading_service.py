import math
import sys
import time
from datetime import datetime

from binance_service import BinanceService
from constants import Symbol, Pair, TradingType
from logger_factory import logger
from results import Trade

DEFAULT_SLEEP_SECOND = 1


class TradingService:
    def __init__(self):
        self._symbol_to_trade = None
        self._open_orders_dict = {}
        self._price_stats_dict = {}
        self._balance_dict = {
            Symbol.USDT: {},
            Symbol.BUSD: {},
            Symbol.USDC: {}
        }
        self._binance_service = BinanceService()

    def _is_price_stats_empty_or_outdated(self, pair):
        stats = self._price_stats_dict.get(pair, None)
        if not stats:
            return True

        timestamp = stats.get("timestamp", None)
        if not timestamp:
            return True

        time_diff = datetime.now() - timestamp
        hours_diff = round(time_diff.total_seconds()) / 3600
        return hours_diff > 4.0

    def _fetch_price_change_statistics(self, pair: str):
        stats = self._binance_service.get_price_change_statistics(pair)
        if stats:
            stats["timestamp"] = datetime.now()
            self._price_stats_dict[pair] = stats

    def _get_sleep_second(self, price: float, target_price: float) -> int:
        return max(round(abs(target_price - price) * 10000), DEFAULT_SLEEP_SECOND)

    def _check_price(self, pair: str) -> tuple[Trade, int]:
        current_price = self._binance_service.get_price(pair)
        if not current_price:
            return None, DEFAULT_SLEEP_SECOND

        if self._is_price_stats_empty_or_outdated(pair):
            self._fetch_price_change_statistics(pair)

        stats = self._price_stats_dict.get(pair, None)
        if not stats:
            return None, DEFAULT_SLEEP_SECOND

        trading_type = TradingType.get_trading_type(pair, self._symbol_to_trade)

        target_price = None
        if trading_type == TradingType.SELL:
            target_price = max(float(stats["high_price"]), 1.0001)
            if current_price >= target_price:
                return Trade(
                    pair=pair,
                    trading_type=TradingType.SELL,
                    quantity=self._calculate_quantity(trading_type, current_price),
                    profit_per_symbol=current_price - 1.0
                ), None

        elif trading_type == TradingType.BUY:
            target_price = min(float(stats["low_price"]), 0.9999)
            if current_price <= target_price:
                return Trade(
                    pair=pair,
                    trading_type=TradingType.BUY,
                    quantity=self._calculate_quantity(trading_type, current_price),
                    profit_per_symbol=1.0 - current_price
                ), None

        return None, self._get_sleep_second(current_price, target_price)

    def _calculate_quantity(self, trading_type: str, price: float) -> float:
        balance = self._balance_dict.get(self._symbol_to_trade, {}).get("free", 0.0)
        if trading_type == TradingType.SELL:
            return balance
        elif trading_type == TradingType.BUY:
            return math.floor(1 / price * balance * 100) / 100

    def _check_profitable_trade(self) -> tuple[Trade, int]:
        max_profitable_trade = None
        min_wait_seconds = sys.maxsize

        for pair in Pair.get_pairs(self._symbol_to_trade):
            trade, wait_seconds = self._check_price(pair)
            if wait_seconds:
                min_wait_seconds = min(wait_seconds, min_wait_seconds)

            elif trade and trade.profit_per_symbol > max_profitable_trade.profit_per_symbol:
                max_profitable_trade = trade

        return max_profitable_trade, min_wait_seconds

    def _update_balance_and_trade_symbol(self):
        self._balance_dict = self._binance_service.fetch_coin_balance_in_wallet(Symbol.ALL)
        self._symbol_to_trade = self._get_dominant_symbol()

    def _update_open_orders(self, pairs):
        self._open_orders_dict = self._binance_service.get_open_orders(pairs)

    def _place_order(self, trade: Trade):
        result = self._binance_service.place_order(
            pair=trade.pair,
            trading_type=trade.trading_type,
            price=trade.pair,
            quantity=trade.quantity
        )
        logger.debug(result)

    def _get_dominant_symbol(self):
        dominant_symbol = None
        dominant_balance = 0.0
        for symbol, value_dict in self._balance_dict.items():
            total_balance = 0.0
            for key, value in value_dict.items():
                total_balance += float(value)

            if not dominant_symbol or total_balance > dominant_balance:
                dominant_symbol = symbol

        return dominant_symbol

    def _check_open_orders(self):
        logger.debug("check open orders")
        while bool(self._open_orders_dict):
            time.sleep(10)
            self._update_open_orders(list(self._open_orders_dict.keys()))
            if not bool(self._open_orders_dict):
                logger.info("orders filled!")
                self._update_balance_and_trade_symbol()
                break

    def _monitor_price(self):
        while True:
            trade, wait_seconds = self._check_profitable_trade()
            if trade:
                self._place_order(trade)
                self._update_open_orders([trade.pair])
                break
            else:
                time.sleep(wait_seconds or DEFAULT_SLEEP_SECOND)

    def start(self):
        self._binance_service.get_trade_fee(Pair.USDC_USDT)
        self._update_balance_and_trade_symbol()
        self._update_open_orders(Pair.ALL)

        logger.info(f"start trading with {self._symbol_to_trade}")

        while True:
            self._check_open_orders()
            self._monitor_price()
