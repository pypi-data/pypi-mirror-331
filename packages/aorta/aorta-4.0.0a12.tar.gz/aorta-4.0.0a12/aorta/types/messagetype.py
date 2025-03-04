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

from .envelope import Envelope


class MessageType(type(pydantic.BaseModel)):
    __module__: str = 'aorta.types'
    __registry__: dict[tuple[str, str], type[Any]]
    envelope_attr: str
    envelope_class: type[Envelope[Any]]
    typename: str

    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **params: Any
    ) -> 'MessageType':
        is_abstract = namespace.pop('__abstract__', False)
        skip_register: bool = namespace.pop('__aorta_disable__', False)
        new_class =  super().__new__(cls, name, bases, namespace, **params) # type: ignore
        namespace.setdefault('__version__', 'v1')
        if not is_abstract:
            k: tuple[str, str] = (namespace['__version__'], name)
            if k in cls.__registry__:
                raise TypeError('Message {0}/{1} is already registered.'.format(*k))
            new_class.__envelope__ = type(
                f'{name}Envelope',
                (cls.envelope_class,), # type: ignore
                {
                    '__annotations__': {
                        cls.envelope_attr: new_class
                    }
                }
            )
            if not skip_register:
                cls.__registry__[k] = new_class.__envelope__ # type: ignore
        
        return new_class # type: ignore