from typing import Protocol

from asd.frontend.client import AgentClient
from asd.kernel import Cmd


class CmdDispatcher(Protocol):
    def __call__(self, cmd: Cmd, /) ->None: ...


def create_msg_broker(client: AgentClient) -> "CmdDispatcher":
    def dispatch(cmd: Cmd, /) ->None:
        client(cmd)
    return dispatch
