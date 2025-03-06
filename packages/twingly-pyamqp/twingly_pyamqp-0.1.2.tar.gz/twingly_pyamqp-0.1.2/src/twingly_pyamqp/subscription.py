import contextlib
import threading
from collections.abc import Callable

from kombu import Queue

from twingly_pyamqp.amqp_config import AMQPconfig
from twingly_pyamqp.amqp_connection import AmqpConnection


class Subscription(AmqpConnection):
    def __init__(self, queue_names: str | list[str], config: AMQPconfig = None):
        self.consuming = threading.Event()
        self.thread = None
        self._thread_lock = threading.Lock()

        if isinstance(queue_names, str):
            queue_names = [queue_names]

        self.queues = [Queue(queue_name) for queue_name in queue_names]

        super().__init__(
            config=config,
        )

    def subscribe(
        self,
        callbacks: Callable[[str, object], None] | list[Callable[[str, object], None]],
        *,
        blocking: bool = True,
        timeout: int | None = None,
        consumer_args: dict | None = None,
    ) -> None:
        if not blocking and timeout is None:
            msg = "timeout must be specified for non-blocking mode"
            raise ValueError(msg)

        with self._thread_lock:
            if self.thread:
                msg = "Only one subscription can be started at a time, multiple queues can be consumed by a single subscription"
                raise ValueError(msg)

            self.consuming.set()
            if blocking:
                with contextlib.suppress(TimeoutError):
                    self._consume_messages(
                        callbacks, consumer_args, blocking=True, timeout=timeout
                    )

            else:
                self.thread = threading.Thread(
                    target=self._consume_messages,
                    args=(callbacks, consumer_args, False, timeout),
                )
                self.thread.daemon = True
                self.thread.start()

    def cancel(self) -> None:
        self.consuming.clear()
        with self._thread_lock:
            if self.thread:
                self.thread.join()
                self.thread = None

    def _consume_messages(self, callbacks, consumer_args, blocking, timeout=5) -> None:
        with self.connection.Consumer(
            self.queues,
            callbacks=callbacks if isinstance(callbacks, list) else [callbacks],
            **(consumer_args or {}),
        ) as _:
            while self.consuming.is_set():
                with (
                    contextlib.nullcontext()
                    if blocking
                    else contextlib.suppress(TimeoutError)
                ):
                    self.connection.drain_events(timeout=timeout)
