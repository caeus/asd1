

import os
import shlex
import shutil
import subprocess
from typing import Final, Optional, Protocol
import venv
from pydantic import Field, TypeAdapter

from pydantic.dataclasses import dataclass

from asd.kernel import WorkspaceAt, WorkspaceConfig


@dataclass
class VenvSetup:
    at: Final[str] = '.venv'
    installs: Final[list[str]] = Field(default_factory=lambda: [])


def create_venv_setup(config: WorkspaceConfig) -> VenvSetup:
    return TypeAdapter(VenvSetup).validate_python(config.data["venv"])


class PyRunner:
    __python_path: Final[str]

    def __init__(self, python_path: str) -> None:
        self.__python_path = python_path
#TEST
    def run(self, args: list[str], cwd: Optional[str] = None) -> None:
        asdasd = [self.__python_path, *args]
        subprocess.check_call(asdasd, cwd=cwd)

    @classmethod
    def create(cls, venv_path: str) -> "PyRunner":
        match os.name:
            case "nt":
                return PyRunner(os.path.join(venv_path, "Scripts", "python.exe"))
            case "posix":
                return PyRunner(os.path.join(venv_path, "bin", "python"))
            case _:
                raise Exception(f"Unknown operating system {os.name}")


class VenvManager(Protocol):
    def delete(self) -> None: ...
    def create(self) -> PyRunner: ...
    def exists(self) -> Optional[PyRunner]: ...


class DefaultVenvManager:
    __setup: Final[VenvSetup]
    __root: Final[str]

    def __init__(self, setup: VenvSetup, root: WorkspaceAt) -> None:
        self.__setup = setup
        self.__root = root

    @property
    def __venv_path(self) -> str:
        return os.path.join(self.__root, self.__setup.at)

    def delete(self) -> None:
        shutil.rmtree(self.__venv_path)
#TEST
    def create(self) -> PyRunner:
        venv.create(self.__venv_path, with_pip=True)
        runner = PyRunner.create(self.__venv_path)
        for dep in self.__setup.installs:
            runner.run(["-m", "pip", "install", *shlex.split(dep)], cwd=self.__root)
        return runner

    def exists(self) -> Optional[PyRunner]:
        if os.path.exists(self.__venv_path):
            return PyRunner.create(self.__venv_path)
        return None


def create_venv_manager(setup: VenvSetup, root: WorkspaceAt) -> VenvManager:
    return DefaultVenvManager(setup, root)
