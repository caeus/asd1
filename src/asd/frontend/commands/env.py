from typing import Final
import click
from dataclasses import dataclass

from asd.frontend.venv_manager import VenvManager


@dataclass(frozen=True)
class EnvCmdHandler:
    impl: Final[click.Command]


def create_env_command(venv_manager: VenvManager) -> EnvCmdHandler:
    @EnvCmdHandler
    @click.command()
    def env() -> None:
        venv_manager.delete()
    return env
