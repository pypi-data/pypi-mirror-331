# Copyright (C) 2016-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import TypeVar

import pydantic

from .envelopedmixin import EnvelopeMixin
from .eventtype import EventType


T = TypeVar('T', bound='Event')


class Event(pydantic.BaseModel, EnvelopeMixin, metaclass=EventType):
    __module__: str = 'aorta.types'
    __message_attr__ = 'data'
    __message_type__ = 'cochise.io/event'