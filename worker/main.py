import sys

from broker.rabbit_client import rabbit_connect


if __name__ == "__main__":
    if len(sys.argv) > 1:
        rabbit_connect(sys.argv[1])
