# Copyright (C) 2016-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import asyncio
import contextlib
import logging
import os
import threading
import time
from queue import Empty
from queue import Queue
from typing import Any
from typing import Iterable

from aorta.types import Acknowledgable
from aorta.types import Envelope
from aorta.types import IMessageHandler
from aorta.types import IPool


class Worker(threading.Thread):
    interval: float = 0.1
    logger: logging.Logger = logging.getLogger('aorta.transport')
    must_exit: bool = False
    queue: Queue[tuple[Acknowledgable, Envelope[Any], Iterable[type[IMessageHandler]]]]

    def __init__(self, pool: IPool):
        self.pool = pool
        self.queue = Queue()
        self.worker_id = bytes.hex(os.urandom(24))
        super().__init__(
            target=self.main_event_loop,
            daemon=True
        )
        self.start()

    def accept_message(self, frame: Acknowledgable):
        import aorta # TODO
        if self.must_exit:
            # Stop accepting messages if we must stop.
            self.logger.debug(
                "Message rejected because the listener is shutting down (id: %s)",
                frame.message_id # type: ignore
            )
            frame.nack()
            return
        envelope = None
        try:
            envelope = aorta.loads(frame.data)
            if envelope is None:
                raise ValueError("Unable to parse message from incoming data.")
        except Exception as e:
            frame.ack()
            self.logger.warning("Caught fatal %s", repr(e))
            return
        assert envelope is not None
        if isinstance(envelope, Envelope):
            self.on_message_received(frame, envelope) # type: ignore
        else:
            frame.nack()
            self.logger.warning(
                "Received unknown Aorta message (kind: %s, uid: %s, id: %s)",
                envelope.kind,
                envelope.metadata.uid[:6],
                envelope.metadata.correlation_id[:6]
            )

    def beat(self):
        pass

    def configure(self) -> None:
        raise NotImplementedError

    @contextlib.contextmanager
    def event_loop(self, envelope: Envelope[Any]):
        loop = asyncio.new_event_loop()
        try:
            yield loop
        except Exception:
            self.logger.exception(
                "Caught fatal %s while handling message (uid: %s, correlation-id: %s)",
                envelope.metadata.uid,
                envelope.metadata.correlation_id
            )
            raise
            return True
        finally:
            if not loop.is_closed():
                assert not loop.is_running()
                loop.close()

    def handle(
        self,
        frame: Acknowledgable,
        envelope: Envelope[Any],
        handlers: Iterable[type[IMessageHandler]]
    ):
        try:
            frame.ack()
            self.logger.debug(
                "Acknowledged incoming message (worker: %s, id: %s)",
                self.ident,
                frame.message_id
            )
        except Exception:
            self.logger.exception("Unable to acknowledge frame (worker: %s)", self.ident)
            return
        return self.run_handlers(envelope, handlers)

    def join(self, timeout: float | None = None):
        self.stop()
        self.logger.debug("Joining worker (id: %s)", self.ident)
        self.queue.join()

    def main_event_loop(self):
        self.logger.debug("Spawning worker (thread: %s)", self.ident)
        self.publisher = self.pool.get_publisher()
        self.runner = self.pool.get_runner(self.publisher)
        self.configure()
        self.logger.debug("Start polling for new messages (thread: %s)", self.ident)
        while True:
            try:
                frame, envelope, handlers = self.queue.get(block=False)
                if self.must_exit:
                    self.logger.debug(
                        "Message rejected because the listener is shutting down (id: %s)",
                        frame.message_id # type: ignore
                    )
                    frame.nack()
                    continue
                self.handle(frame, envelope, handlers)
                self._beat()
            except Empty:
                time.sleep(0.1)
                if self.must_exit:
                    break
            except Exception as e:
                self.logger.exception("Caught fatal %s while handling message", type(e).__name__)
            time.sleep(self.interval)
        self._beat()
        self.logger.debug("Worker complete (id: %s, dropped: %s)", self.ident, self.queue.qsize())

    def on_message_received(
        self,
        frame: Acknowledgable,
        envelope: Envelope[Any],
    ):
        import aorta # TODO
        self.queue.put((frame, envelope, aorta.get(envelope)))

    def run_handlers(
        self,
        envelope: Envelope[Any],
        handlers: Iterable[type[IMessageHandler]]
    ):
        with self.event_loop(envelope) as loop:
            loop.run_until_complete(self.execute(envelope, handlers))

    def stop(self):
        self.must_exit = True
        return self

    async def execute(
        self,
        envelope: Envelope[Any],
        handlers: Iterable[type[IMessageHandler]]
    ) -> None:
        return await self.runner.run(
            publisher=self.publisher,
            envelope=envelope,
            handlers=handlers
        )

    def _beat(self):
        try:
            self.beat()
        except Exception as e:
            self.logger.exception("Caught fatal %s while handling message", type(e).__name__)