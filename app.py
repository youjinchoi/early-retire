import time

from binance_service import BinanceService
from constants import Symbol, Pair
from logger_factory import logger

logger.info("start early-retire!")

binance_service = BinanceService()

symbol = Pair.BUSD_USDT

symbol_to_buy = Symbol.BUSD
symbol_to_sell = Symbol.USDT
total_coin_count = initial_coin_count = 10000

TARGET_BUY_PRICE = 0.999
TARGET_SELL_PRICE = 1
TARGET_AMOUNT = 10000

sleep_second = 1

while True:
    price = binance_service.get_price(symbol)

    if not price:
        logger.warning(f"invalid price for {symbol}. {price=}")
        continue

    if symbol_to_buy == Symbol.BUSD and price <= TARGET_BUY_PRICE:
        logger.info(f"target hit to buy {symbol_to_buy}. {price=}")
        result = binance_service.place_order(
            symbol_to_buy, symbol_to_sell, price, float(TARGET_AMOUNT)
        )
        if result.is_success:
            total_coin_count = (
                result.symbol_to_buy_balance + result.symbol_to_sell_balance
            )
            logger.info(
                f"order filled. now have {result.symbol_to_buy_balance} {result.symbol_to_buy} and {result.symbol_to_sell_balance} {result.symbol_to_sell}. total {total_coin_count} stable coins"
            )
            symbol_to_sell = Symbol.BUSD
            symbol_to_buy = Symbol.USDT

        sleep_second = (TARGET_SELL_PRICE - price) * 10000

    elif symbol_to_sell == Symbol.BUSD and price >= TARGET_SELL_PRICE:
        logger.info(f"target hit to sell {symbol_to_sell}. {price=}")
        result = binance_service.place_order(
            symbol_to_buy, symbol_to_sell, price, float(TARGET_AMOUNT)
        )
        if result.is_success:
            total_coin_count = (
                result.symbol_to_buy_balance + result.symbol_to_sell_balance
            )
            logger.info(
                f"order filled. now have {result.symbol_to_buy_balance} {result.symbol_to_buy} and {result.symbol_to_sell_balance} {result.symbol_to_sell}. total {total_coin_count} stable coins"
            )
            symbol_to_sell = Symbol.USDT
            symbol_to_buy = Symbol.BUSD
        sleep_second = (price - TARGET_BUY_PRICE) * 10000
    else:
        sleep_second = (
            (price - TARGET_BUY_PRICE) * 10000
            if symbol_to_sell == Symbol.USDT
            else (TARGET_SELL_PRICE - price) * 10000
        )

    time.sleep(round(sleep_second))
