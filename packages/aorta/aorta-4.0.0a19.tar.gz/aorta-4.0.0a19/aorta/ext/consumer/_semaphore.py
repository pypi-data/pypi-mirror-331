# Copyright (C) 2016-2025 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import uuid
import threading
import time
import logging
from types import TracebackType


class Semaphore(threading.Semaphore):
    logger: logging.Logger = logging.getLogger('aorta.handler')

    def __enter__(self): # type: ignore
        lock_id = str(uuid.uuid4())
        t0 = time.monotonic()
        self.logger.debug(
            "Acquiring concurrency lock (id: %s)",
            lock_id
        )
        result = self.acquire()
        td = time.monotonic() - t0
        self.logger.debug(
            "Acquired concurrency lock in %.05f (id: %s)",
            td,
            lock_id,
        )
        return result

    def __exit__(
        self,
        cls: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None
    ) -> None:
        return self.release()