# Copyright (C) 2016-2025 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import logging.config
import os
from typing import Any
from typing import TypeVar
from queue import SimpleQueue

import fastapi
from libcanonical.runtime import MainProcess # type: ignore

from aorta import Command
from aorta import Event
from aorta import MessagePublisher
from aorta import NullTransport
from aorta.types import Acknowledgable
from aorta.types import Envelope
from aorta.types import IPublisher
from aorta.types import IRunner
from ._threadpool import ThreadPool
from ._pool import Pool


E = TypeVar('E', bound=Command|Event)


class BaseConsumer(MainProcess):
    __module__: str = 'aorta.ext.consumer'
    concurrency: int = 1
    debug: bool = False
    interval = 0.01
    pool: Pool
    queue: SimpleQueue[tuple[Acknowledgable, Envelope[Any]]]

    def __init__(self, name: str, concurrency: int = 1, **kwargs: Any):
        super().__init__(name=name)
        self.concurrency = concurrency
        if os.getenv('WORKER_CONCURRENCY') and str.isdigit(os.environ['WORKER_CONCURRENCY']):
            self.concurrency = int(os.environ['WORKER_CONCURRENCY'])

    def acknowledge(self, message: Acknowledgable) -> None:
        raise NotImplementedError

    def configure(self, reloading: bool = False):
        self.logger.debug("Running with %s workers", self.concurrency)
        if not reloading:
            self.publisher = self.get_publisher()
            self.queue = SimpleQueue()
            self.pool = ThreadPool(
                publisher=self.publisher,
                queue=self.queue,
                concurrency=self.concurrency,
                debug=self.debug,
                initializer=self.configure_worker
            )

    def configure_worker(self) -> None:
        logging.config.dictConfig(dict(self.get_logging_config()))

    def get_publisher(self) -> IPublisher:
        return MessagePublisher(
            transport=NullTransport()
        )

    def get_runner(
        self,
        publisher: IPublisher,
        frame: Acknowledgable,
        request: fastapi.Request | None = None,
        **kwargs: Any
    ) -> IRunner:
        raise NotImplementedError

    def on_message(
        self,
        frame: Acknowledgable,
        envelope: Envelope[Any]
    ) -> None:
        raise NotImplementedError

    def route(self, envelope: Envelope[E]) -> list[str]:
        """Return a list of strings indicating the topics that the
        `envelope` must be sent to. Subclasses must override this
        method.
        """
        raise NotImplementedError

    async def main_event(self) -> None:
        pass

    async def teardown(self) -> None:
        await self.pool.join()

    def _acknowledge(self, message: Acknowledgable, envelope: Envelope[Any]) -> None:
        try:
            self.acknowledge(message)
        except Exception:
            self.logger.exception(
                "Unable to ACK message (uid: %s, correlatio-id: %s)",
                envelope.metadata.uid,
                envelope.metadata.correlation_id,
            )