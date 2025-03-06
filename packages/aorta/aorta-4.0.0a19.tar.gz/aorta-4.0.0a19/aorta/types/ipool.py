# Copyright (C) 2016-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Protocol

from .ipublisher import IPublisher
from .irunner import IRunner


class IPool(Protocol):
    __module__: str = 'aorta.types'

    def get_publisher(self) -> IPublisher:
        ...

    def get_runner(self, publisher: IPublisher) -> IRunner:
        ...