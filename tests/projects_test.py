





def test_akjshd(): ...


# FakeProjects = NewType("FakeProjects", MappingProxyType[ProjectId, Project])


# class FakeModuleCtx:
#     project_id: Final[ProjectId]
#     module_id: Final[ModuleId]
#     _tasks: dict[TaskId, Task]

#     def __init__(self,
#                  project_id: ProjectId,
#                  module_id: ModuleId, tasks: dict[TaskId, Task]):
#         self.project_id = project_id
#         self.module_id = module_id
#         self._tasks = tasks

#     def task(self, *deps: str)->Callable[[TaskAction],None]:
#         def config(action: TaskAction) -> None:
#             tid = TaskId(action.__name__)
#             self._tasks[tid] = Task(id=tid,
#                                     action=action,
#                                     deps={
#                 TaskRef.parse(ref=ref, current_module=self.module_id,
#                               current_project=self.project_id)
#                 for ref in deps
#             }
#             )
#         return config


# class MockProjectCtx:
#     project_id:Final[ProjectId]
#     _modules: dict[ModuleId, Module]

#     def __init__(self, project_id:ProjectId,modules: dict[ModuleId, Module]):
#         self.project_id=project_id
#         self._modules = modules

#     def module(self, mod: Callable[[FakeModuleCtx], None]) -> None:
#         mid = ModuleId(mod.__name__)
#         tasks: dict[TaskId, Task] = {}
#         ctx = FakeModuleCtx(
#             module_id=mid,
#             project_id=self.project_id,
#             tasks=tasks)
#         mod(ctx)
#         self._modules[mid] = Module(id=mid, tasks=MappingProxyType(tasks))
#     ...


# class MockWorkspaceCtx:
#     _projects: dict[ProjectId, Project]

#     def __init__(self, projects: dict[ProjectId, Project]):
#         self._projects = projects

#     def project(self, id: str)->Callable[[Callable[[MockProjectCtx], None]],None]:
#         def config(proj: Callable[[MockProjectCtx], None]) -> None:
#             pid = ProjectId(id)
#             modules: dict[ModuleId, Module] = {}
#             ctx = MockProjectCtx(project_id=pid,modules=modules)
#             proj(ctx)
#             self._projects[pid] = Project(
#                 id=pid, modules=MappingProxyType(modules))
#         return config
