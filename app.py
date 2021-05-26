from logger_factory import logger
from trading_service import TradingService

logger.info("start early-retire!")

while True:
    try:
        TradingService().start()
    except Exception:
        logger.exception("unexpected error while running early-retire")
