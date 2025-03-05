# Copyright (C) 2016-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

import pydantic
import pydantic.main

from .eventenvelope import EventEnvelope
from .messageheader import MessageHeader
from .messagetype import MessageType


class UnknownEventEnvelope(EventEnvelope[Any]):
    data: dict[str, Any]

    def is_known(self) -> bool:
        return False


class EventType(MessageType):
    __module__: str = 'aorta.types'
    __registry__: dict[tuple[str, str], type[EventEnvelope[Any]]] = {}
    envelope_attr: str = 'data'
    envelope_class: type[EventEnvelope[Any]] = EventEnvelope
    typename: str = 'cochise.io/event'

    @staticmethod
    def parse(data: Any) -> EventEnvelope[Any] | MessageHeader | None:
        header = None
        try:
            header = MessageHeader.model_validate(data)
            if header.type == EventType.typename:
                return EventType.__registry__[(header.api_version, header.kind)].model_validate(data)
        except KeyError:
            return UnknownEventEnvelope.model_validate(data)
        except (pydantic.ValidationError, TypeError, ValueError):
            return header