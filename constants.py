from typing import Final


class Symbol:
    USDT: Final = "USDT"
    BUSD: Final = "BUSD"
    USDC: Final = "USDC"
    ALL: Final = [USDT, BUSD, USDC]


class Pair:
    BUSD_USDT: Final = f"{Symbol.BUSD}{Symbol.USDT}"
    USDC_BUSD: Final = f"{Symbol.USDC}{Symbol.BUSD}"
    USDC_USDT: Final = f"{Symbol.USDC}{Symbol.USDT}"
    ALL: Final = [BUSD_USDT, USDC_BUSD, USDC_USDT]

    @staticmethod
    def get_pairs(symbol: str) -> list[str]:
        if symbol == Symbol.USDT:
            return [Pair.BUSD_USDT, Pair.USDC_USDT]
        elif symbol == Symbol.BUSD:
            return [Pair.BUSD_USDT, Pair.USDC_BUSD]
        elif symbol == Symbol.USDC:
            return [Pair.USDC_USDT, Pair.USDC_BUSD]
        else:
            return None


class TradingType:
    BUY: Final = "BUY"
    SELL: Final = "SELL"

    @staticmethod
    def get_trading_type(pair: str, symbol: str):
        if pair.startswith(symbol):
            return TradingType.SELL
        elif pair.endswith(symbol):
            return TradingType.BUY
        else:
            return None
