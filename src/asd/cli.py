

import asyncio
from dataclasses import dataclass
import os
from typing import Awaitable, Callable, Final, NewType, Optional, Protocol, Set, TypeVar
from injector import Injector, inject

from wcmatch.glob import GLOBSTAR, glob
from asd.api import ModuleId, ProjectId, TaskId, TaskRef, WorkspaceAt
from asd.bind import Bind, ConfigureModule
from asd.runner import TaskRegistry, task_registry, task_runner
from asd.server import PROJECT_MARKER, WORSPACE_MARKER, project_loader, project_registry



CWD = NewType("CWD", str)


def cwd() -> CWD:
    return CWD(os.getcwd())




def workspace_at(cwd: CWD) -> WorkspaceAt:
    current = os.path.abspath(cwd)
    while not os.path.exists(os.path.join(current, WORSPACE_MARKER)):
        parent = os.path.dirname(current)
        if parent == current:
            raise Exception(
                f"Reached root of file system, couldn't find a folder with a {WORSPACE_MARKER} file")
        current = parent
    return WorkspaceAt(current)



WorkingPath = NewType("WorkingPath", ProjectId)


def working_path(cwd: CWD, workspace_at: WorkspaceAt) -> WorkingPath:
    return WorkingPath(ProjectId(os.path.relpath(cwd, workspace_at)))


QueryStr = NewType("QueryStr", str)


@dataclass(frozen=True)
class QueryParts:
    project_glob: Final[Optional[str]]  # type:ignore
    module: Final[ModuleId]  # type:ignore
    task: Final[TaskId]  # type:ignore

    @classmethod
    def from_query(cls, query: QueryStr) -> "QueryParts":
        parts = query.split(":")
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
                raise Exception(f"Wrong query format {query}")


MatchedProjects = NewType("MatchedProjects", Set[ProjectId])


class ProjectFinder(Protocol):
    def __call__(self, parts: QueryParts,/) -> MatchedProjects: ...


def project_finder(workspace_at: WorkspaceAt, working_path: WorkingPath) -> ProjectFinder:
    def find(parts: QueryParts) -> MatchedProjects:
        project_glob = parts.project_glob
        if project_glob is None:
            return MatchedProjects({working_path})
        else:
            marker_size = PROJECT_MARKER.__len__()
            return MatchedProjects({
                ProjectId(marker[:-marker_size])
                for marker in
                glob(
                    os.path.join(project_glob, PROJECT_MARKER),
                    root_dir=workspace_at,
                    flags=GLOBSTAR
                )
            })
    return find


def matched_projects(finder: ProjectFinder, parts: QueryParts) -> MatchedProjects:
    return finder(parts)


MatchedTasks = NewType("MatchedTasks", Set[TaskRef])


def matched_tasks(matched_projects: MatchedProjects,
                  parts: QueryParts,
                  task_registry: TaskRegistry
                  ) -> MatchedTasks:
    result = set()
    for project in matched_projects:
        ref = TaskRef(
            project=project,
            module=parts.module,
            task=parts.task
        )
        if task_registry(ref) is not None:
            result.add(ref)

    return MatchedTasks(result)


@Bind.module
def _noop_module(bind: Bind) -> None:
    ...


@Bind.module
def cli_module(bind: Bind) -> None:
    bind.singleton(cwd)
    bind.singleton(workspace_at)
    bind.singleton(working_path)
    bind.singleton(project_finder)
    bind.singleton(matched_projects)
    bind.singleton(QueryParts.from_query)
    bind.singleton(project_loader)
    bind.singleton(project_registry)
    bind.singleton(task_registry)
    bind.singleton(matched_tasks)
    bind.singleton(task_runner)


T = TypeVar('T')


class CliRunner(Protocol):
    async def __call__(self, callable: Callable[..., Awaitable[T]],/) -> T: ...


def cli_runner(input_module: ConfigureModule = _noop_module) -> CliRunner:
    injector=Injector([cli_module, input_module], auto_bind=False)
    def runner(callable:Callable[..., Awaitable[T]],/)->T:
        return asyncio.run( injector.call_with_injection(inject(callable)))
    return runner