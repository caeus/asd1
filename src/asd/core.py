











# class Workspace:
#     _root: Final[WorkspaceRoot]
#     _loader: Final[ProjectLoader]
#     _projects: dict[ProjectId, Optional[Project]]

#     def __init__(self,
#                  root: WorkspaceRoot,
#                  loader: ProjectLoader,
#                  projects: dict[ProjectId, Optional[Project]]):
#         self._root = root
#         self._loader = loader
#         self._projects = projects

#     def __contains__(self, path: ProjectId) -> bool:
#         package = self.get(path)
#         return package is not None

#     def __getitem__(self, path: ProjectId) -> Project:
#         package = self.get(path)
#         if package is None:
#             raise Exception(
#                 f"package {path} doesn't have a {PROJECT_MARKER} file")
#         return package

#     def get(self, path: ProjectId) -> Optional[Project]:
#         if path in self._projects:
#             return self._projects[path]
#         package = self._loader.load(path)
#         self._projects[path] = package
#         return package
    







#Plan = NewType("Plan", MappingProxyType[TaskRef, Task])


# class Planner:
#     _workspace: Final[Workspace]

#     def __init__(self, workspace: Workspace) -> None:
#         self._workspace = workspace

#     def get(self, ref: TaskRef) -> Optional[Task]:
#         project = self._workspace.get(ref.project)
#         if project is None:
#             return None
#         module = project.get(ref.module)
#         if module is None:
#             return None
#         return module.get(ref.task)

#     def plan_for(self, refs: Set[TaskRef]) -> Plan:
#         raw_plan: dict[TaskRef, Task] = {}

#         def include(ref: TaskRef, trace: list[TaskRef]) -> None:
#             if ref in raw_plan:
#                 return
#             if ref in trace:
#                 raise Exception(f"Circular dependency found trace: {trace}")
#             task = self.get(ref)
#             if task is None:
#                 raise Exception(f"Task {ref} doesn't exist")
#             raw_plan[ref] = task
#             for dep in task.deps:
#                 include(dep, [ref, *trace])
#         for ref in refs:
#             include(ref, [])
#         return Plan(MappingProxyType(raw_plan))


# class TaskRunner:
#     _root: Final[WorkspaceRoot]  # type:ignore
#     _workspace: Final[Workspace]
#     _results: Final[dict[TaskRef, Hashable]]

#     def __init__(self, workspace: Workspace):
#         self._workspace = workspace
#         self._results = {}

#     def __contains__(self, ref: TaskRef) -> bool:
#         return self.get(ref) is not None

#     def get(self, ref: TaskRef) -> Optional[Task]:
#         project = self._workspace.get(ref.project)
#         if project is None:
#             return None
#         module = project.get(ref.module)
#         if module is None:
#             return None
#         return module.get(ref.task)

#     def _run(self, ref: TaskRef, trace: List[TaskRef]) -> Any:
#         if ref in trace:
#             raise Exception(
#                 f"Circular task dependency involving tasks {trace}")
#         if ref in self._results:
#             return self._results[ref]
#         print(f"Will run task {ref}")
#         task = self.get(ref)
#         if task is None:
#             raise Exception(f"task {ref} doesn't exist")
#         new_trace = [ref, *trace]
#         for dep in task.deps:
#             self._run(dep, new_trace)
#         result = task.action(TaskCtx(
#             workspace=self._root,
#             project=ref.project
#         ))
#         self._results[ref] = result
#         return result

#     def run(self, ref: TaskRef) -> Any:
#         return self._run(ref, [])


# @Bind.module
# def asd_imodule(bind: Bind) -> None:
#     @bind.singleton
#     def _() -> CWD:
#         return CWD(os.getcwd())
#     bind.singleton(workspace_root)
#     bind.singleton(project_id)

#     bind.singleton(Planner)

#     @bind.singleton
#     def _(root: WorkspaceRoot, loader: ProjectLoader) -> Workspace:
#         return Workspace(root=root, loader=loader, projects={})

#     @bind.singleton
#     def _(root: WorkspaceRoot) -> ProjectLoader:
#         return DefaultProjectLoader(root)
#     bind.singleton(TaskRunner)


# @Bind.module
# def _noop_module(bind: Bind) -> None: ...


# def asd_injector(override: ConfigureModule = _noop_module) -> Injector:
#     return Injector([asd_imodule, override], auto_bind=False)
