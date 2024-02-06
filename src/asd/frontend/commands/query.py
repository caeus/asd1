from typing import Final
from dataclasses import dataclass
import click

from asd.frontend.dispatcher import CmdDispatcher
from asd.kernel import QueryCmd, TaskQuery


@dataclass(frozen=True)
class QueryCmdHandler:
    impl: Final[click.Command]


def create_query_command(dispatcher: CmdDispatcher) -> QueryCmdHandler:
    @QueryCmdHandler
    @click.command()
    @click.argument('query')
    def query(query: str) -> None:
        dispatcher(QueryCmd(TaskQuery.from_str(query)))
    return query
