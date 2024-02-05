

import asyncio
import sys
from typing import Protocol

from pydantic import TypeAdapter

from asd.backend.tasks.service import TasksService
from asd.kernel import RunCmd


class Cli(Protocol):
    def __call__(self) -> None: ...


def create_cli(service: TasksService) -> Cli:
    def cli() -> None:
        op = sys.argv[1]
        match op:
            case 'run':
                asyncio.run(service(TypeAdapter(RunCmd).validate_json(sys.argv[2])))
            case _:
                raise Exception(f"Unknown op {op}")
    return cli
