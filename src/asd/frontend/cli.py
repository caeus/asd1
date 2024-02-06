

import click
from asd.frontend.commands.env import EnvCmdHandler
from asd.frontend.commands.query import QueryCmdHandler
from asd.frontend.commands.run import RunCmdHandler


def create_cli(
        run: RunCmdHandler,
        env: EnvCmdHandler,
        query: QueryCmdHandler
) -> click.Group:
    @click.group()
    def cli() -> None: ...
    cli.add_command(run.impl)
    cli.add_command(env.impl)
    cli.add_command(query.impl)
    return cli
