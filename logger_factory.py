import logging

logger = logging.getLogger("app")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
