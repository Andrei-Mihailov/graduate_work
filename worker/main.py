from rabbit_client import RabbitMq


def main() -> None:
    rabbit: RabbitMq = RabbitMq()
    rabbit.run()


main()