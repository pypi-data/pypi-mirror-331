# Copyright (C) 2016-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import logging
import uuid
from typing import Any

from .types import Envelope
from .types import IPublisher
from .types import MessageMetadata
from .types import Publishable


class Transaction:
    __module__: str = 'aorta'
    correlation_id: str
    logger: logging.Logger = logging.getLogger('canonical')
    messages: list[Envelope[Any]]
    publisher: IPublisher

    def __init__(
        self,
        publisher: IPublisher,
        metadata: MessageMetadata | None = None,
        correlation_id: str | None = None
    ):
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.messages = []
        self.metadata = metadata
        self.publisher = publisher

    def issue(
        self,
        message: Publishable,
        correlation_id: str | None = None,
        audience: set[str] | None = None
    ):
        return self.publish(message, correlation_id=correlation_id, audience=audience)

    def get_correlation_id(self) -> str:
        cid = self.correlation_id
        if self.metadata:
            cid = self.metadata.correlation_id
        return cid

    def pending(self) -> list[Publishable]:
        return [x.message for x in self.messages]

    def publish(
        self,
        message: Publishable,
        correlation_id: str | None = None,
        audience: set[str] | None = None
    ):
        envelope = message.envelope(
            correlation_id=correlation_id or self.correlation_id,
            audience=audience
        )
        self.logger.debug(
            "Adding %s to running transaction (uid: %s, correlation-id: %s)",
            type(message).__name__,
            envelope.metadata.uid,
            envelope.metadata.correlation_id
        )
        self.messages.append(envelope)

    def rollback(self) -> None:
        self.messages = []

    async def send(self, message: Publishable) -> None:
        envelope = message.envelope(correlation_id=self.get_correlation_id())
        await self.publisher.send([envelope])

    async def commit(self) -> None:
        """Immediately publishes pending messages to the messaging
        infrastructure.
        """
        self.logger.debug(
            "Committed %s messages (uid: %s, correlation-id: %s)",
            len(self.messages),
            self.metadata.uid if self.metadata else 'None',
            self.correlation_id
        )
        await self.publisher.send(self.messages)
        self.messages = []

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, cls: type[BaseException] | None, *args: Any):
        if cls is not None:
            self.rollback()
            return
        await self.commit()