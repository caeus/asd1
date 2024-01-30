import os
import runpy
from types import MappingProxyType
from typing import Any, Final, Optional, Protocol, TypeGuard

from asd.api import ModuleCtx, ModuleId, ProjectId, Task, TaskId, WorkspaceAt


PROJECT_MARKER = "__project__.py"
WORSPACE_MARKER = "__workspace__.toml"

class Module:
    id: Final[ModuleId]
    _tasks: Final[MappingProxyType[TaskId, Task]]

    def __init__(self, id: ModuleId, tasks: MappingProxyType[TaskId, Task]) -> None:
        self._tasks = tasks
        self.id = id

    def get(self, id: TaskId) -> Optional[Task]:
        return self._tasks.get(id)

    def __getitem__(self, id: TaskId) -> Task:
        task = self.get(id)
        if task is None:
            raise Exception(f"Project {self.id} doesn't contain task {id}")
        return task


class Project:
    id: Final[ProjectId]
    _modules: MappingProxyType[ModuleId, Module]

    def __init__(self, id: ProjectId, modules: MappingProxyType[ModuleId, Module]) -> None:
        self.id = id
        self._modules = modules

    def get(self, id: ModuleId) -> Optional[Module]:
        return self._modules.get(id)

    def __getitem__(self, id: ModuleId) -> Module:
        project = self.get(id)
        if project is None:
            raise Exception(f"Project {self.id} doesn't have module {id}")
        return project






    

    
class ProjectLoader(Protocol):
    def __call__(self, project_id: ProjectId,/) -> Optional[Project]: ...

def project_loader(workspace_at:WorkspaceAt)->ProjectLoader:
    def load(project_id:ProjectId,/)->Optional[Project]:
        marker = os.path.join(workspace_at, project_id, PROJECT_MARKER)
        if os.path.exists(marker):
            project_raw = runpy.run_path(
                marker,
                run_name=project_id)
            def build_module(configure: ASDModuleConfig) -> Module:
                id = ModuleId(configure.__name__)
                tasks: dict[TaskId, Task] = {}
                ctx = ModuleCtx(
                    id=id,
                    project=project_id,
                    workspace=workspace_at,
                    tasks=tasks
                )
                configure(ctx)
                return Module(id=id, tasks=MappingProxyType(tasks))
            modules = MappingProxyType({ModuleId(val.__name__): build_module(val)
                                        for val in project_raw.values()
                                        if is_asd_module_config(val)
                                        })
            return Project(id=project_id,
                           modules=modules)
        else:
            return None
        ...
    return load


class ProjectRegistry(Protocol):
    def __call__(self, id: ProjectId) -> Optional[Project]: ...


def project_registry(loader:ProjectLoader) -> ProjectRegistry:
    projects:dict[ProjectId,Optional[Project]] = {} 
    def get(id: ProjectId) -> Optional[Project]:
        if id in projects:
            return projects[id]
        project=loader(id)
        projects[id]=project
        return project
    return get

class ASDObject(Protocol):
    __asd_kind__: str


class ModuleConfig(Protocol):
    __name__: str
    def __call__(self, ctx: ModuleCtx, /) -> None: ...


class ASDModuleConfig(ASDObject, ModuleConfig):
    ...

ASD_OBJECT_MARKER = "__asd_kind__"

def is_asd_object(any: Any) -> TypeGuard[ASDObject]:
    return hasattr(any, ASD_OBJECT_MARKER)



def is_asd_module_config(any: Any) -> TypeGuard[ASDModuleConfig]:
    return callable(any) and is_asd_object(any) and any.__asd_kind__ == "project"