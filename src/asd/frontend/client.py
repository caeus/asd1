

from typing import Protocol

from pydantic import RootModel

from asd.frontend.venv_manager import VenvManager
from asd.kernel import Cmd


class AgentClient(Protocol):
    def __call__(self, cmd: Cmd) -> None: ...


def create_agent_client(manager: VenvManager) -> AgentClient:
    def send(cmd: Cmd) -> None:
        runner = manager.exists()
        if not runner:
            runner = manager.create()
        runner.run(["-m", "asd.backend", cmd.op,
                   RootModel[Cmd](cmd).model_dump_json()])
    return send
