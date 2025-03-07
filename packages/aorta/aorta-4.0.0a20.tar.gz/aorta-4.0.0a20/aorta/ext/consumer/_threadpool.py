# Copyright (C) 2016-2025 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import asyncio
import threading
import time
from typing import Any
from typing import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures.thread import BrokenThreadPool
from queue import Queue

import aorta
from aorta.runners import SequentialRunner
from aorta.types import Acknowledgable
from aorta.types import Envelope
from aorta.types import IRunner
from aorta.types import IPublisher
from ._pool import Pool
from ._semaphore import Semaphore


class ThreadPool(Pool):
    must_exit: bool = False
    step: int = 0

    def __init__(
        self,
        publisher: IPublisher,
        queue: Queue[tuple[Acknowledgable, Envelope[Any]]],
        concurrency: int = 1,
        debug: bool = False,
        runner: IRunner | None = None,
        initializer: Callable[..., None] | None = None
    ) -> None:
        super().__init__(queue=queue, concurrency=concurrency, debug=debug)
        self.initializer = initializer or (lambda: None)
        self.executor = ThreadPoolExecutor(
            max_workers=concurrency,
            initializer=self.initializer
        )
        self.publisher = publisher
        self.thread = threading.Thread(
            daemon=True,
            target=self.main_event_loop
        )
        self.runner = runner or SequentialRunner()
        self.thread.start()
        self.semaphore = Semaphore(value=self.concurrency)

    def stop(self):
        self.must_exit = True

    def main_event_loop(self):
        self.logger.debug("Starting pool manager thread.")
        while True:
            time.sleep(0.1)
            self.step += 1
            self.main_event()
            if self.must_exit:
                break

    def main_event(self) -> None:
        try:
            if not self.semaphore.acquire(blocking=False):
                return
            frame, envelope = self.queue.get(block=True, timeout=1.0)
        except Exception:
            self.semaphore.release()
            return
        try:
            self.executor.submit(
                self.run,
                ack=lambda x: x.ack(),
                runner=self.runner,
                publisher=self.publisher,
                frame=frame,
                envelope=envelope
            )
        except BrokenThreadPool:
            self.logger.error("Pool is broken, reinitializing.")
            self.executor.shutdown(wait=False, cancel_futures=False)
            self.executor = ThreadPoolExecutor(
                max_workers=self.concurrency,
                initializer=self.initializer
            )
            self.executor.submit(
                self.run,
                ack=lambda x: x.ack(),
                runner=self.runner,
                publisher=self.publisher,
                frame=frame,
                envelope=envelope
            )
        except RuntimeError:
            # This is raised if shutdown() was called.
            pass
        except Exception as e:
            self.logger.exception(
                "Caught fatal %s (uid: %s, correlation-id: %s)",
                type(e).__name__,
                envelope.metadata.uid,
                envelope.metadata.correlation_id,
            )

    def run(
        self,
        ack: Callable[[Acknowledgable], None],
        runner: IRunner,
        publisher: IPublisher,
        frame: Acknowledgable,
        envelope: Envelope[Any],
    ) -> None:
        loop = None
        try:
            loop = asyncio.new_event_loop()
            c = runner.run(
                publisher=publisher,
                frame=frame,
                envelope=envelope,
                handlers=aorta.get(envelope)
            )
            loop.run_until_complete(c)
        finally:
            self.semaphore.release()
            if loop is not None and loop.is_running():
                loop.close()

    async def join(self):
        self.queue.join()
        self.must_exit = True
        self.executor.shutdown(wait=True, cancel_futures=False)
        self.thread.join()