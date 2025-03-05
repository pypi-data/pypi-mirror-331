# Copyright (C) 2016-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import json
from typing import Any

from .baserunner import BaseRunner
from .commandhandler import CommandHandler
from .eventlistener import EventListener
from .localrunner import LocalRunner
from .messagehandler import MessageHandler
from .messagepublisher import MessagePublisher
from .nulltransport import NullTransport
from .ping import Pong
from .ping import Ping
from .ping import PingHandler
from .ping import OnPingPonged
from .provider import Provider
from .transaction import Transaction
from .sewer import Sewer
from .types import Command
from .types import Event
from .types import HandlerException
from . import types


__all__: list[str] = [
    'get',
    'parse',
    'register',
    'types',
    'BaseRunner',
    'Command',
    'CommandHandler',
    'Event',
    'EventListener',
    'HandlerException',
    'LocalRunner',
    'MessageHandler',
    'MessagePublisher',
    'NullTransport',
    'Ping',
    'Pong',
    'Provider',
    'Sewer',
    'Transaction',
]


get = Provider.get
register = Provider.register


def loads(buf: str | bytes):
    return parse(json.loads(buf))


def parse(data: Any) -> types.Envelope[Any] | types.MessageHeader | None:
    """Parses a datastructure into a registered message type
    declaration. Return the evelope or ``None``.
    """
    return (
        types.EventType.parse(data) or
        types.CommandType.parse(data)
    )


register(PingHandler)
register(OnPingPonged)