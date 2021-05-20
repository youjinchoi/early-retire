from typing import Final


class Symbol:
    USDT: Final = "USDT"
    BUSD: Final = "BUSD"


class Pair:
    BUSD_USDT: Final = f"{Symbol.BUSD}{Symbol.USDT}"


class OrderType:
    BUY: Final = "buy"
    SELL: Final = "sell"
