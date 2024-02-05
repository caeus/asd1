import click
from injector import Injector
from asd.kernel import create_workspace_config, get_cwd, get_workspace_location
from asd.kernel.bind import Bind, ConfigureModule
from asd.frontend.dispatcher import create_msg_broker
from asd.frontend.client import create_agent_client
from asd.frontend.venv_manager import create_venv_manager, create_venv_setup
from asd.frontend.cli import create_cli
from asd.frontend.commands.env import create_launcher_command
from asd.frontend.commands.run import create_run_command


@Bind.module
def launcher_module(bind:Bind)->None:
    bind.singleton(create_cli)
    bind.singleton(create_run_command)
    bind.singleton(create_launcher_command)
    bind.singleton(create_msg_broker)
    bind.singleton(create_agent_client)
    bind.singleton(create_venv_manager)
    bind.singleton(create_venv_setup)
    bind.singleton(create_workspace_config)
    bind.singleton(get_workspace_location)
    bind.singleton(get_cwd)

def application(override:list[ConfigureModule]=[])->click.Group:
    injector=Injector([launcher_module,*override],auto_bind=False)
    return injector.get(click.Group)

def main()->None:
    application()()
