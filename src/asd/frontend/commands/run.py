from typing import Final
from dataclasses import dataclass
import click

from asd.frontend.dispatcher import CmdDispatcher
from asd.kernel import RunCmd, TaskQuery, WorkspaceAt

@dataclass(frozen=True)
class RunCmdHandler:
    impl:Final[click.Command]
def create_run_command(dispatcher:CmdDispatcher,workspace_at:WorkspaceAt)->RunCmdHandler:
    @RunCmdHandler
    @click.command()
    @click.argument('query')
    def run(query:str)->None:
        print(workspace_at)
        print(workspace_at)
        print(workspace_at)
        print(workspace_at)
        print(workspace_at)
        print(workspace_at)
        print(workspace_at)
        dispatcher(RunCmd(TaskQuery.from_str(query)))
    return run