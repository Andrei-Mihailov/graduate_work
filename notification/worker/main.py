from db.rabbit_client import RabbitMq
from db.store import Store


def main() -> None:
    store: Store = Store()
    store.init_db()
    rabbit: RabbitMq = RabbitMq()
    rabbit.run()


main()
