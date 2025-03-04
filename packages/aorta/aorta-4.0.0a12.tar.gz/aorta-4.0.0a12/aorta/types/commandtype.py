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

from .commandenvelope import CommandEnvelope
from .messageheader import MessageHeader
from .messagetype import MessageType


class UnknownCommandEnvelope(CommandEnvelope[Any]):
    spec: dict[str, Any]

    def is_known(self) -> bool:
        return False


class CommandType(MessageType):
    __module__: str = 'aorta.types'
    __registry__: dict[tuple[str, str], type[CommandEnvelope[Any]]] = {}
    envelope_attr: str = 'spec'
    envelope_class: type[CommandEnvelope[Any]] = CommandEnvelope
    typename: str = 'cochise.io/command'

    @staticmethod
    def parse(data: Any) -> CommandEnvelope[Any] | MessageHeader | None:
        header = None
        try:
            header = MessageHeader.model_validate(data)
            if header.type == CommandType.typename:
                return CommandType.__registry__[(header.api_version, header.kind)].model_validate(data)
        except KeyError:
            return UnknownCommandEnvelope.model_validate(data)
        except (pydantic.ValidationError, TypeError, ValueError):
            return header