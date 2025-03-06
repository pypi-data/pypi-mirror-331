import os

from dotenv import load_dotenv

load_dotenv()


class AMQPconfig:
    def __init__(
        self,
        rabbitmq_host: str | None = None,
        rabbitmq_port: int | None = None,
        amqp_user: str | None = None,
        amqp_password: str | None = None,
    ):
        self.rabbitmq_host = rabbitmq_host or os.getenv("RABBITMQ_N_HOST", "localhost")
        self.rabbitmq_port = rabbitmq_port or int(os.getenv("RABBITMQ_PORT", "5672"))
        self.amqp_user = amqp_user or os.getenv("AMQP_USERNAME", "guest")
        self.amqp_password = amqp_password or os.getenv("AMQP_PASSWORD", "guest")

    def connection_url(self):
        return f"amqp://{self.amqp_user}:{self.amqp_password}@{self.rabbitmq_host}:{self.rabbitmq_port}"
