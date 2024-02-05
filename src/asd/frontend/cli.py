




import click
from asd.frontend.commands.env import EnvCmdHandler
from asd.frontend.commands.run import RunCmdHandler


def create_cli(
        run:RunCmdHandler,
        launcher:EnvCmdHandler
)->click.Group:
    @click.group()
    def cli()->None: ...
    cli.add_command(run.impl)
    cli.add_command(launcher.impl)
    return cli
    
    