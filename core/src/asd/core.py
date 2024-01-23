from dataclasses import dataclass
import os
import runpy
from types import MappingProxyType
from typing import Any, Callable, Final, Hashable, List, Never, NewType, Optional, Protocol, Set, Type, TypeGuard


PACKAGE_MARKER = "__package__.py"
WORSPACE_MARKER = "__workspace__.toml"

WorkspaceRoot = NewType('WorkspaceRoot', str)


@dataclass
class TaskRef:
    package: str
    project: str
    task: str

    def __hash__(self) -> int:
        return (self.package, self.project, self.task).__hash__()

    @classmethod
    def parse(cls: Type["TaskRef"], ref: str,
              current_package: Optional[str] = None,
              current_project: Optional[str] = None) -> "TaskRef":
        def error(
        ) -> Never: raise Exception(f"wrongly formatted task ref {ref}")

        parts = list(reversed(ref.split(":")))
        if len(parts) == 0:
            error()
        task = parts[0]
        if len(parts) > 1:
            project = parts[1]
        elif current_project is not None:
            project = current_project
        else:
            error()
        if len(parts) == 3:
            package = parts[2]
        elif current_package is not None:
            package = current_package
        else:
            error()
        return cls(package=package, project=project, task=task)


class TaskCtx:
    workspace: Final[WorkspaceRoot]
    package: Final[str]

    def __init__(self,
                 workspace: WorkspaceRoot,
                 package: str,
                 ) -> None:
        self.workspace = workspace
        self.package = package

    @property
    def location(self) -> str:
        return os.path.join(self.workspace, self.package)


class TaskAction(Protocol):
    __name__: str
    def __call__(self, ctx: TaskCtx) -> Hashable: ...


@dataclass
class Task:
    id: Final[str]  # type: ignore
    deps: Final[Set[TaskRef]]  # type: ignore
    action: Final[TaskAction]  # type: ignore


class Project:
    id: Final[str]
    _tasks: Final[MappingProxyType[str, Task]]

    def __init__(self, id: str, tasks: MappingProxyType[str, Task]) -> None:
        self._tasks = tasks
        self.id = id

    def get(self, id: str) -> Optional[Task]:
        return self._tasks.get(id)

    def __getitem__(self, id: str) -> Task:
        task = self.get(id)
        if task is None:
            raise Exception(f"Project {self.id} doesn't contain task {id}")
        return task


class Package:
    id: Final[str]
    _projects: MappingProxyType[str, Project]

    def __init__(self, id: str, projects: MappingProxyType[str, Project]) -> None:
        self.id = id
        self._projects = projects

    def get(self, id: str) -> Optional[Project]:
        return self._projects.get(id)

    def __getitem__(self, id: str) -> Project:
        project = self.get(id)
        if project is None:
            raise Exception(f"Package {self.id} doesn't have project {id}")
        return project


class PackageLoader:
    root: Final[WorkspaceRoot]

    def __init__(self, root: WorkspaceRoot) -> None:
        self.root = root

    def load(self, path: str) -> Optional[Package]:
        package_path = os.path.join(self.root, path, PACKAGE_MARKER)
        if os.path.exists(package_path):
            package_raw = runpy.run_path(
                package_path,
                run_name=path)

            def build_project(configure: FabricProjectConfiguration) -> Project:
                id = configure.__name__
                tasks: dict[str, Task] = {}
                ctx = ProjectCtx(
                    id=id,
                    package=path,
                    workspace=self.root,
                    tasks=tasks
                )
                configure(ctx)
                return Project(id=id, tasks=MappingProxyType(tasks))

            projects = MappingProxyType({val.__name__: build_project(val)
                                        for val in package_raw.values()
                                        if _is_fabric_project_configuration(val)
                                         })
            return Package(id=path,
                           projects=projects)
        else:
            return None


class Workspace:
    root: Final[WorkspaceRoot]
    _loader: PackageLoader
    _packages: dict[str, Optional[Package]]

    def __init__(self, loader: PackageLoader, packages: dict[str, Optional[Package]]):
        self.root = loader.root
        self._loader = loader
        self._packages = packages

    def __contains__(self, path: str) -> bool:
        package = self.get(path)
        return package is not None

    def __getitem__(self, path: str) -> Package:
        package = self.get(path)
        if package is None:
            raise Exception(
                f"package {path} doesn't have a {PACKAGE_MARKER} file")
        return package

    def get(self, path: str) -> Optional[Package]:
        if path in self._packages:
            return self._packages[path]
        package = self._loader.load(path)
        self._packages[path] = package
        return package

    @classmethod
    def at(cls, root: WorkspaceRoot) -> "Workspace":
        return cls(loader=PackageLoader(root), packages={})


class TaskRunner:
    _root: Final[WorkspaceRoot]  # type:ignore
    _workspace: Final[Workspace]
    _results: Final[dict[TaskRef, Hashable]]

    def __init__(self, workspace: Workspace):
        self._workspace = workspace
        self._results = {}

    def __contains__(self, ref: TaskRef) -> bool:
        return self.get(ref) is not None

    def get(self, ref: TaskRef) -> Optional[Task]:
        package = self._workspace.get(ref.package)
        if package is None:
            return None
        project = package.get(ref.project)
        if project is None:
            return None
        return project.get(ref.task)

    def _run(self, ref: TaskRef, trace: List[TaskRef]) -> Any:
        if ref in trace:
            raise Exception(
                f"Circular task dependency involving tasks {trace}")
        if ref in self._results:
            return self._results[ref]
        print(f"Will run task {ref}")
        task = self.get(ref)
        if task is None:
            raise Exception(f"task {ref} doesn't exist")
        new_trace = [ref, *trace]
        for dep in task.deps:
            self._run(dep, new_trace)
        result = task.action(TaskCtx(
            workspace=self._workspace.root,
            package=ref.package
        ))
        self._results[ref] = result
        return result

    def run(self, ref: TaskRef) -> Any:
        return self._run(ref, [])


class ProjectCtx:
    _tasks: Final[dict[str, Task]]
    id: Final[str]
    package: Final[str]
    workspace: Final[WorkspaceRoot]

    def __init__(self, id: str,
                 package: str,
                 workspace: WorkspaceRoot,
                 tasks: dict[str, Task]):
        self.id = id
        self.package = package
        self.workspace = workspace
        self._tasks = tasks

    def __setitem__(self, key: str, value: Task) -> None:
        self._tasks[key] = value

    def task(self, *deps: str) -> Callable[[TaskAction], None]:

        def decorator(action: TaskAction) -> None:
            self[action.__name__] = Task(
                id=action.__name__,
                deps={TaskRef.parse(ref=dep,
                                    current_package=self.package,
                                    current_project=self.id) for dep in deps},
                action=action
            )
        return decorator

    @property
    def folder(self) -> str:
        return os.path.join(self.workspace, self.package)


class ProjectConfiguration(Protocol):
    __name__: str
    def __call__(self, ctx: ProjectCtx, /) -> None: ...


class FabricObject(Protocol):
    __fabric_kind__: str


class FabricProjectConfiguration(FabricObject, ProjectConfiguration):
    ...


def _is_fabric_object(any: Any) -> TypeGuard[FabricObject]:
    return hasattr(any, "__fabric_kind__")


def _is_fabric_project_configuration(any: Any) -> TypeGuard[FabricProjectConfiguration]:
    return callable(any) and _is_fabric_object(any) and any.__fabric_kind__ == "project"

def project(configure: ProjectConfiguration) -> FabricProjectConfiguration:
    setattr(configure, "__fabric_kind__", "project")
    if _is_fabric_project_configuration(configure):
        return configure
    raise Exception("This won't ever happen, but beware...")
