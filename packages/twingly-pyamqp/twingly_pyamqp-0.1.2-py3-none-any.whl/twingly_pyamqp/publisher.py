from kombu import Exchange

from twingly_pyamqp.amqp_config import AMQPconfig
from twingly_pyamqp.amqp_connection import AmqpConnection


class Publisher(AmqpConnection):
    def __init__(
        self,
        exchange_name: str | None = None,
        routing_key: str | None = None,
        config: AMQPconfig = None,
    ):
        super().__init__(
            config=config,
        )
        self.exchange = Exchange(exchange_name)
        self.connection.routing_key = routing_key

    def publish(
        self,
        payload: object,
        routing_key: str | None = None,
        publish_args: dict | None = None,
    ):
        if not routing_key and not self.connection.routing_key:
            msg = "Routing key must be specified"
            raise ValueError(msg)

        self.connection.Producer(serializer="json").publish(
            payload,
            exchange=self.exchange,
            routing_key=routing_key or self.connection.routing_key,
            **(publish_args or {}),
        )
