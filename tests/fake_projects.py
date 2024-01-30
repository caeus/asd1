

from types import MappingProxyType
from typing import Callable, Final, NewType, Optional

from wcmatch.glob import GLOBSTAR, globmatch

from asd.api import ModuleId, ProjectId, Task, TaskAction, TaskId, TaskRef
from asd.bind import Bind, ConfigureModule
from asd.cli import MatchedProjects, ProjectFinder, QueryParts, WorkingPath
from asd.server import Module, Project, ProjectLoader


FakeProjects = NewType("FakeProjects", MappingProxyType[ProjectId, Project])


class FakeModuleCtx:
    project_id: Final[ProjectId]
    module_id: Final[ModuleId]
    _tasks: dict[TaskId, Task]

    def __init__(self,
                 project_id: ProjectId,
                 module_id: ModuleId, tasks: dict[TaskId, Task]):
        self.project_id = project_id
        self.module_id = module_id
        self._tasks = tasks

    def task(self, *deps: str)->Callable[[TaskAction],None]:
        def config(action: TaskAction) -> None:
            tid = TaskId(action.__name__)
            self._tasks[tid] = Task(id=tid,
                                    action=action,
                                    deps={
                TaskRef.parse(ref=ref, current_module=self.module_id,
                              current_project=self.project_id)
                for ref in deps
            }
            )
        return config


class FakeProjectCtx:
    project_id:Final[ProjectId]
    _modules: dict[ModuleId, Module]

    def __init__(self, project_id:ProjectId,modules: dict[ModuleId, Module]):
        self.project_id=project_id
        self._modules = modules

    def module(self, mod: Callable[[FakeModuleCtx], None]) -> None:
        mid = ModuleId(mod.__name__)
        tasks: dict[TaskId, Task] = {}
        ctx = FakeModuleCtx(
            module_id=mid,
            project_id=self.project_id,
            tasks=tasks)
        mod(ctx)
        self._modules[mid] = Module(id=mid, tasks=MappingProxyType(tasks))
    ...


class FakeWorkspaceCtx:
    _projects: dict[ProjectId, Project]

    def __init__(self, projects: dict[ProjectId, Project]):
        self._projects = projects

    def project(self, id: str)->Callable[[Callable[[FakeProjectCtx], None]],None]:
        def config(proj: Callable[[FakeProjectCtx], None]) -> None:
            pid = ProjectId(id)
            modules: dict[ModuleId, Module] = {}
            ctx = FakeProjectCtx(project_id=pid,modules=modules)
            proj(ctx)
            self._projects[pid] = Project(
                id=pid, modules=MappingProxyType(modules))
        return config


def fake_workspace(work: Callable[[FakeWorkspaceCtx], None]) -> FakeProjects:
    projects: dict[ProjectId, Project] = {}
    ctx = FakeWorkspaceCtx(projects)
    work(ctx)
    return FakeProjects(MappingProxyType(projects))


def fake_project_finder(fake_projects: FakeProjects,working_path:WorkingPath) -> ProjectFinder:
    def find(query: QueryParts) -> MatchedProjects:
        pattern = query.project_glob
        if pattern:
            return MatchedProjects({project for project in fake_projects.keys()
                                    if globmatch(project, pattern, flags=GLOBSTAR)})
        else:
            return MatchedProjects({working_path})
    return find


def fake_project_loader(fake_projects: FakeProjects) -> ProjectLoader:
    def load(project_id: ProjectId) -> Optional[Project]:
        return fake_projects.get(project_id)

    return load



def fake_workspace_module(work: Callable[[FakeWorkspaceCtx], None])->ConfigureModule:
    fake_projects=fake_workspace(work)
    @Bind.module
    def test_module(bind: Bind) -> None:
        bind.singleton(fake_project_finder)
        bind.singleton(fake_project_loader)
        @bind.singleton
        def _()->FakeProjects:
            return fake_projects
    return test_module





