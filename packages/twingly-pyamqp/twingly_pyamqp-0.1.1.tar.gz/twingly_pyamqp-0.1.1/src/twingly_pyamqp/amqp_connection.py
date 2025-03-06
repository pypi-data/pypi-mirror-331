from kombu import Connection, Exchange, Queue

from twingly_pyamqp.amqp_config import (
    AMQPconfig,
)


class AmqpConnection:
    def __init__(
        self,
        config: AMQPconfig = None,
    ):
        self.config = config or AMQPconfig()
        self.connection = Connection(self.config.connection_url())

    def declare_queue(
        self,
        queue_name: str,
        exchange_name: str | None = None,
        routing_key: str | None = None,
        exchange_opts: dict | None = None,
        queue_opts: dict | None = None,
    ):
        if not exchange_name and routing_key:
            msg = "Default exchange cannot have a routing key"
            raise ValueError(msg)

        exchange = Exchange(exchange_name or "", **(exchange_opts or {}))
        queue = Queue(
            queue_name,
            exchange=exchange,
            routing_key=routing_key or queue_name,
            **(queue_opts or {}),
        )
        bound_queue = queue(self.connection)
        bound_queue.declare()

    def declare_exchange(
        self,
        exchange_name: str,
        exchange_opts: dict | None = None,
    ):
        exchange = Exchange(exchange_name, **(exchange_opts or {}))
        bound_exchange = exchange(self.connection)
        bound_exchange.declare()
