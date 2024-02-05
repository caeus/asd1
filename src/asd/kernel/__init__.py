import os
import tomllib
from types import MappingProxyType
from typing import Any, Final, NewType, Optional

from dataclasses import dataclass


PROJECT_MARKER = "__project__.py"

WORSPACE_MARKER = "__workspace__.toml"

CWD = NewType("CWD", str)
def get_cwd() -> CWD:
    return CWD(os.getcwd())
WorkspaceAt = NewType("WorkspaceAt", str)

def get_workspace_location(cwd: CWD) -> WorkspaceAt:
    current = os.path.abspath(cwd)
    while not os.path.exists(os.path.join(current, WORSPACE_MARKER)):
        parent = os.path.dirname(current)
        if parent == current:
            raise Exception(
                f"Reached root of file system, couldn't find a folder with a {WORSPACE_MARKER} file")
        current = parent
    return WorkspaceAt(current)


ProjectId = NewType("ProjectId", str)
ModuleId = NewType("ModuleId", str)
TaskId = NewType("TaskId", str)


@dataclass(frozen=True)
class WorkspaceConfig:
    data: Final[MappingProxyType[str, Any]]


def create_workspace_config(at: WorkspaceAt) -> WorkspaceConfig:
    with open(os.path.join(at, WORSPACE_MARKER), "rb") as content:
        return WorkspaceConfig(MappingProxyType(tomllib.load(content)))


@dataclass(frozen=True)
class TaskQuery:
    project_glob: Final[Optional[str]]
    module: Final[ModuleId]
    task: Final[TaskId]

    @classmethod
    def from_str(cls, raw: str) -> "TaskQuery":
        parts = raw.split(":")
        match len(parts):
            case 2:
                return cls(
                    project_glob=None,
                    module=ModuleId(parts[0]),
                    task=TaskId(parts[1])
                )
            case 3:
                return cls(
                    project_glob=parts[0],
                    module=ModuleId(parts[1]),
                    task=TaskId(parts[2])
                )
            case _:
                raise Exception(f"Wrong query format {raw}")


@dataclass(frozen=True)
class RunCmd:
    tasks: Final[TaskQuery]


Cmd = RunCmd
