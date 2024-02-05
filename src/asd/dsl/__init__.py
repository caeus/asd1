

from dataclasses import dataclass
import os
from types import MappingProxyType
from typing import Any, Callable, Final, Hashable, NewType, Protocol, Set, TypeGuard
from asd.kernel import CWD, ModuleId, ProjectId, TaskId, WorkspaceAt


WorkingPath = NewType("WorkingPath", ProjectId)


def get_working_path(cwd: CWD, workspace_at: WorkspaceAt) -> WorkingPath:
    return WorkingPath(ProjectId(os.path.relpath(cwd, workspace_at)))




@dataclass(frozen=True)
class TaskRef:
    project: Final[ProjectId]
    module: Final[ModuleId]
    task: Final[TaskId]

    @classmethod
    def parse(cls, ref: str, current_project: ProjectId, current_module: ModuleId,) -> "TaskRef":
        parts = ref.split(":")
        match len(parts):
            case 3:
                return cls(project=ProjectId(parts[0]),
                           module=ModuleId(parts[1]),
                           task=TaskId(parts[2]))
            case 2:
                return cls(project=current_project,
                           module=ModuleId(parts[0]),
                           task=TaskId(parts[1]))
            case 1:
                return cls(project=current_project,
                           module=current_module,
                           task=TaskId(parts[0]))
            case _:
                raise Exception(f"Wrong ref format {ref}")


class TaskCtx:
    workspace: Final[WorkspaceAt]
    project: Final[ProjectId]
    module: Final[ModuleId]
    id: Final[TaskId]
    _deps: Final[MappingProxyType[TaskRef, Hashable]]

    def __init__(self,
                 id: TaskId,
                 module: ModuleId,
                 project: ProjectId,
                 workspace: WorkspaceAt,
                 deps: MappingProxyType[TaskRef, Hashable]) -> None:
        self.workspace = workspace
        self.project = project
        self.module = module
        self.id = id
        self._deps = deps

    @property
    def location(self) -> str:
        return os.path.join(self.workspace, self.project)


class TaskAction(Protocol):
    __name__: str
    async def __call__(self, ctx: TaskCtx) -> Hashable: ...


@dataclass(frozen=True)
class Task:
    id: Final[str]
    deps: Final[Set[TaskRef]]
    action: Final[TaskAction]


class ModuleCtx:
    _tasks: Final[dict[TaskId, Task]]
    id: Final[ModuleId]
    project: Final[ProjectId]
    workspace: Final[WorkspaceAt]

    def __init__(self,
                 id: ModuleId,
                 project: ProjectId,
                 workspace: WorkspaceAt,
                 tasks: dict[TaskId, Task]):
        self.id = id
        self.project = project
        self.workspace = workspace
        self._tasks = tasks

    def __setitem__(self, key: TaskId, value: Task) -> None:
        self._tasks[key] = value

    def task(self, *deps: str) -> Callable[[TaskAction], None]:

        def decorator(action: TaskAction) -> None:
            self[TaskId(action.__name__)] = Task(
                id=action.__name__,
                deps={TaskRef.parse(ref=dep,
                                    current_module=self.id,
                                    current_project=self.project) for dep in deps},
                action=action
            )
        return decorator

    @property
    def folder(self) -> str:
        return os.path.join(self.workspace, self.project)


class ASDObject(Protocol):
    __asd_kind__: str


class ModuleConfig(Protocol):
    __name__: str
    def __call__(self, ctx: ModuleCtx, /) -> None: ...


class ASDModuleConfig(ASDObject, ModuleConfig):
    __asd_kind__: str
    __name__: str
    def __call__(self, ctx: ModuleCtx, /) -> None: ...


ASD_OBJECT_MARKER = "__asd_kind__"

def is_asd_object(any: Any) -> TypeGuard[ASDObject]:
    return hasattr(any, ASD_OBJECT_MARKER)

def is_asd_module_config(any: Any) -> TypeGuard[ASDModuleConfig]:
    return callable(any) and is_asd_object(any) and any.__asd_kind__ == "project"


def module(configure: ModuleConfig) -> ASDModuleConfig:
    setattr(configure, ASD_OBJECT_MARKER, "project")
    if is_asd_module_config(configure):
        return configure
    raise Exception("This won't ever happen, but beware...")
