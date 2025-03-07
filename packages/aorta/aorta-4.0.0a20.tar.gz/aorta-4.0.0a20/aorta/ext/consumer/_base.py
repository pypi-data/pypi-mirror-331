# Copyright (C) 2016-2025 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import logging
import logging.config
import time
import os
from typing import Any
from typing import TypeVar

from libcanonical.runtime import MainProcess # type: ignore

from aorta import Command
from aorta import Event
from aorta import MessagePublisher
from aorta import NullTransport
from aorta.types import Envelope
from aorta.types import IPublisher
from aorta.types import IRunner
from aorta.pool import ThreadWorker

E = TypeVar('E', bound=Command|Event)


class BaseConsumer(MainProcess):
    __module__: str = 'aorta.ext.consumer'
    concurrency: int = 1
    debug: bool = False
    interval = 0.1
    logger: logging.Logger = logging.getLogger('aorta.transport.ingress')
    metrics: logging.Logger = logging.getLogger('aorta.metrics')
    workers: list[ThreadWorker]

    def __init__(self, name: str, concurrency: int = 1, **kwargs: Any):
        super().__init__(name=name)
        self.concurrency = concurrency
        if os.getenv('WORKER_CONCURRENCY') and str.isdigit(os.environ['WORKER_CONCURRENCY']):
            self.concurrency = int(os.environ['WORKER_CONCURRENCY'])
        self.workers = []

    def configure(self, reloading: bool = False):
        self.logger.debug("Running with %s workers", self.concurrency)
        if not reloading:
            self.publisher = self.get_publisher()
            for _ in range(self.concurrency):
                self.workers.append(self.initialize_worker())

    def configure_worker(self) -> None:
        logging.config.dictConfig(dict(self.get_logging_config()))

    def get_publisher(self) -> IPublisher:
        return MessagePublisher(
            transport=NullTransport()
        )

    def get_runner(self, publisher: IPublisher) -> IRunner:
        raise NotImplementedError

    def initialize_worker(self) -> ThreadWorker:
        raise NotImplementedError

    def route(self, envelope: Envelope[E]) -> list[str]:
        """Return a list of strings indicating the topics that the
        `envelope` must be sent to. Subclasses must override this
        method.
        """
        raise NotImplementedError

    def main_event(self) -> None:
        time.sleep(1)

    def teardown(self):
        self.logger.debug("Tearing down listener")
        for worker in map(ThreadWorker.stop, self.workers):
            self.logger.debug("Closing worker (id: %s)", worker.ident)

        # TODO: pretty ugly
        t0 = time.monotonic()
        while any([w.is_alive() for w in self.workers]):
            time.sleep(1)
            if (time.monotonic() - t0) > 180:
                break
        self.logger.debug("Done")