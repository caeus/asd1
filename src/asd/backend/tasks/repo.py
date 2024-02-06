import os
import runpy
from types import MappingProxyType
from typing import Final, Optional, Protocol, Set

from wcmatch import glob
from asd.dsl import ASDModuleConfig, ModuleCtx, Task, TaskRef, WorkingPath, is_asd_module_config

from asd.kernel import PROJECT_MARKER, ModuleId, ProjectId, TaskId, TaskQuery, WorkspaceAt


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
    def __call__(self, project_id: ProjectId, /) -> Optional[Project]: ...


def create_project_loader(workspace_at: WorkspaceAt) -> ProjectLoader:
    def load(project_id: ProjectId, /) ->Optional[Project]:
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


class ProjectsRepo(Protocol):
    def query(self, query: str) -> Set[ProjectId]: ...

    def get(self, id: ProjectId) -> Optional[Project]: ...


class DefaultProjectsRepo:
    __root__: Final[WorkspaceAt]
    __loader__: Final[ProjectLoader]
    __projects__: Final[dict[ProjectId, Optional[Project]]]

    def __init__(self, root: WorkspaceAt, loader: ProjectLoader) -> None:
        self.__root__ = root
        self.__loader__ = loader
        self.__projects__ = {}
        pass

    def query(self, query: str) -> Set[ProjectId]:
        marker_size = PROJECT_MARKER.__len__()
        return {
            ProjectId(marker[:-marker_size])
            for marker in
            glob.glob(
                os.path.join(query, PROJECT_MARKER),
                root_dir=self.__root__,
                flags=glob.GLOBSTAR
            )
        }

    def get(self, id: ProjectId) -> Optional[Project]:
        if id in self.__projects__:
            return self.__projects__[id]
        project = self.__loader__(id)
        self.__projects__[id] = project
        return project

    @classmethod
    def create(cls,  root: WorkspaceAt, loader: ProjectLoader) -> ProjectsRepo:
        return cls(root, loader)


class TasksRepo(Protocol):
    def query(self, query: TaskQuery) -> Set[TaskRef]: ...
    def get(self, ref: TaskRef) -> Optional[Task]: ...


class DefaultTasksRepo:
    __projects__: Final[ProjectsRepo]
    __working_path__: Final[WorkingPath]

    def __init__(self, project: ProjectsRepo, working_path: WorkingPath) -> None:
        self.__projects__ = project
        self.__working_path__ = working_path

    def get(self, ref: TaskRef) -> Optional[Task]:
        project = self.__projects__.get(ref.project)
        if project is None:
            return None
        module = project.get(ref.module)
        if module is None:
            return None
        return module.get(ref.task)

    def query(self, query: TaskQuery) -> Set[TaskRef]:
        glob = query.project_glob
        if glob is not None:
            projects = self.__projects__.query(glob)
        else:
            projects = {self.__working_path__}
        result: Set[TaskRef] = set()
        for project_id in projects:
            ref = TaskRef(project=project_id,
                          module=query.module,
                          task=query.task)
            task = self.get(ref)
            if task is not None:
                result.add(ref)
        return result

    @classmethod
    def create(cls, project: ProjectsRepo, working_path: WorkingPath) -> TasksRepo:
        return cls(project=project, working_path=working_path)
