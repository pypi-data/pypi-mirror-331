# Copyright (C) 2016-2025 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import logging
from typing import Any
#from typing import Callable
from queue import Queue

#import fastapi

from aorta.types import Acknowledgable
from aorta.types import Envelope
from aorta.types import IRunner
#from aorta.types import IPublisher


class Pool:
    logger: logging.Logger = logging.getLogger('canonical')
    runner: IRunner

    def __init__(
        self,
        queue: Queue[tuple[Acknowledgable, Envelope[Any]]],
        concurrency: int = 1,
        debug: bool = False
    ) -> None:
        self.concurrency = concurrency
        self.debug = debug
        self.queue = queue

    def stop(self) -> None:
        raise NotImplementedError

    async def join(self) -> None:
        raise NotImplementedError

    #async def submit(
    #    self,
    #    ack: Callable[..., None],
    #    runner: IRunner,
    #    publisher: IPublisher,
    #    frame: Acknowledgable,
    #    envelope: Envelope[Any],
    #    request: fastapi.Request | None = None
    #) -> None:
    #    raise NotImplementedError