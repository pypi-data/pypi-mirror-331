# Copyright (C) 2016-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import os
from concurrent.futures import CancelledError
from typing import TYPE_CHECKING

from google.cloud.pubsub_v1 import SubscriberClient # type: ignore
from google.cloud.pubsub_v1.subscriber.futures import StreamingPullFuture # type: ignore

from aorta.pool import ThreadWorker
if TYPE_CHECKING:
    from ._topiclistener import TopicListener


class PubsubWorker(ThreadWorker):
    streamer: StreamingPullFuture
    pool: 'TopicListener'

    def __init__(
        self,
        pool: 'TopicListener',
        prefetch: int = 2
    ):
        super().__init__(pool)
        self.prefetch = prefetch

    def beat(self) -> None:
        if not self.must_exit:
            try:
                self.streamer.result(timeout=0.5)
            except CancelledError:
                self.logger.warning("Broker connection stream was cancelled.")
            except TimeoutError:
                pass
            except Exception as e:
                self.logger.critical(
                    "Caught fatal %s on broker connection.",
                    type(e).__name__
                )
                self.must_exit = True

        if self.must_exit and self.streamer.running():
            self.logger.debug("Cancelling leases with Google Pubsub")
            self.streamer.cancel()

    def configure(self) -> None:
        self.subscription_id = os.environ['GOOGLE_PUBSUB_SUBSCRIPTION']
        self.subscriber = SubscriberClient()
        self.streamer = self.subscriber.subscribe( # type: ignore
            self.subscription_id,
            self.accept_message,
            flow_control=self.pool.get_flow_control()
        )

        self.logger.debug("Established connection to subscription %s", self.subscription_id)