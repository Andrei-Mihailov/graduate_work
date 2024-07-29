import sys

from loguru import logger


if __name__ == "__main__":
    if len(sys.argv) > 1:
        from broker.rabbit_client import rabbit_connect

        rabbit_connect(sys.argv[1])
    else:
        logger.error("Не указан параметр для запуска воркера")
