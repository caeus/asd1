from dataclasses import dataclass
import os
from types import MappingProxyType
from typing import Callable, Final, Hashable, NewType, Protocol, Set


WorkspaceAt = NewType("WorkspaceAt", str)
ProjectId = NewType("ProjectId", str)
ModuleId = NewType("ModuleId", str)
TaskId = NewType("TaskId", str)


@dataclass(frozen=True)
class TaskRef:
    project: Final[ProjectId]  # type:ignore
    module: Final[ModuleId]  # type:ignore
    task: Final[TaskId]  # type:ignore

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
    id:Final[TaskId]
    _deps: Final[MappingProxyType[TaskRef, Hashable]]  
    def __init__(self,
                 id:TaskId,
                 module:ModuleId,
                 project:ProjectId,
                 workspace:WorkspaceAt,
                 deps:MappingProxyType[TaskRef, Hashable]) -> None:
        self.workspace=workspace
        self.project=project
        self.module=module
        self.id=id
        self._deps=deps

    @property
    def location(self) -> str:
        return os.path.join(self.workspace, self.project)


class TaskAction(Protocol):
    __name__: str
    async def __call__(self, ctx: TaskCtx) -> Hashable: ...


@dataclass(frozen=True)
class Task:
    id: Final[str]  # type: ignore
    deps: Final[Set[TaskRef]]  # type: ignore
    action: Final[TaskAction]  # type: ignore


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
