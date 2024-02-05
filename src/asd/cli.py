# import asyncio
# import os
# from typing import Awaitable, Callable, NewType, Protocol, Set
# from injector import Injector, inject

# from wcmatch.glob import GLOBSTAR, glob
# from asd.kernel import CWD, PROJECT_MARKER, ProjectId, TaskQuery, WorkspaceAt, get_cwd, get_workspace_location
# from asd.kernel.bind import Bind, ConfigureModule
# from asd.runner import TaskRegistry, task_registry, task_runner
# from asd.server import  project_loader, project_registry

# WorkingPath = NewType("WorkingPath", ProjectId)


# def working_path(cwd: CWD, workspace_at: WorkspaceAt) -> WorkingPath:
#     return WorkingPath(ProjectId(os.path.relpath(cwd, workspace_at)))

# QueryStr = NewType("QueryStr", str)

# MatchedProjects = NewType("MatchedProjects", Set[ProjectId])


# class ProjectFinder(Protocol):
#     def __call__(self, query: TaskQuery,/) -> MatchedProjects: ...


# def project_finder(workspace_at: WorkspaceAt, working_path: WorkingPath) -> ProjectFinder:
#     def find(parts: TaskQuery) -> MatchedProjects:
#         project_glob = parts.project_glob
#         if project_glob is None:
#             return MatchedProjects({working_path})
#         else:
#             marker_size = PROJECT_MARKER.__len__()
#             return MatchedProjects({
#                 ProjectId(marker[:-marker_size])
#                 for marker in
#                 glob(
#                     os.path.join(project_glob, PROJECT_MARKER),
#                     root_dir=workspace_at,
#                     flags=GLOBSTAR
#                 )
#             })
#     return find


# def matched_projects(finder: ProjectFinder, parts: TaskQuery) -> MatchedProjects:
#     return finder(parts)


# MatchedTasks = NewType("MatchedTasks", Set[TaskRef])


# def matched_tasks(matched_projects: MatchedProjects,
#                   parts: TaskQuery,
#                   task_registry: TaskRegistry
#                   ) -> MatchedTasks:
#     result = set()
#     for project in matched_projects:
#         ref = TaskRef(
#             project=project,
#             module=parts.module,
#             task=parts.task
#         )
#         if task_registry(ref) is not None:
#             result.add(ref)

#     return MatchedTasks(result)


# @Bind.module
# def _noop_module(bind: Bind) -> None:
#     ...


# @Bind.module
# def cli_module(bind: Bind) -> None:
#     bind.singleton(get_cwd)
#     bind.singleton(get_workspace_location)
#     bind.singleton(working_path)
#     bind.singleton(project_finder)
#     bind.singleton(matched_projects)
#     bind.singleton(TaskQuery.from_str)
#     bind.singleton(project_loader)
#     bind.singleton(project_registry)
#     bind.singleton(task_registry)
#     bind.singleton(matched_tasks)
#     bind.singleton(task_runner)




# class CliRunner(Protocol):
#     async def __call__[X:object](self, callable: Callable[..., Awaitable[X]],/) -> X: ...


# def cli_runner(input_module: ConfigureModule = _noop_module) -> CliRunner:
#     injector=Injector([cli_module, input_module], auto_bind=False) 
#     def runner[T:object](callable:Callable[..., Awaitable[T]],/)->T: 
#         return asyncio.run(injector.call_with_injection(inject(callable))) #type:ignore
#     return runner #type:ignore