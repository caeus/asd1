from typing import Final
from dataclasses import dataclass
import click

from asd.frontend.dispatcher import CmdDispatcher
from asd.kernel import PlanCmd, TaskQuery


@dataclass(frozen=True)
class PlanCmdHandler:
    impl: Final[click.Command]


def create_plan_command(dispatcher: CmdDispatcher) -> PlanCmdHandler:
    @PlanCmdHandler
    @click.command()
    @click.argument('query')
    def plan(query: str) -> None:
        dispatcher(PlanCmd(TaskQuery.from_str(query)))
    return plan
