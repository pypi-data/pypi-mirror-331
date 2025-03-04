# Copyright (C) 2016-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import ClassVar
from typing import Self

import pydantic

from .envelope import Envelope


class Message(pydantic.BaseModel):
    __abstract__: bool = True
    __envelope__: type[Envelope[Any]]
    __message_attr__: ClassVar[str]

    def envelope(
        self,
        correlation_id: str | None = None,
        audience: set[str] | None = None,
        labels: dict[str, str | None] | None = None,
        annotations: dict[str, str | None] | None = None,
        namespace: str = ''
    ) -> Envelope[Self]:
        return self.__envelope__.model_validate({
            'apiVersion': getattr(self, '__version__', 'v1'),
            'kind': type(self).__name__,
            'type': 'unimatrixone.io/command',
            'metadata': {
                'annotations': annotations or {},
                'audience': audience or set(),
                'correlationId': correlation_id,
                'labels': labels or {},
                'namespace': namespace
            },
            self.__message_attr__: self.model_dump()
        })