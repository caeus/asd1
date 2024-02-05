

# import asyncio
# from asyncio import Task as Promise
# from types import MappingProxyType
# from typing import Hashable, NewType, Optional, Protocol, Set, Tuple

# from asd.api import Task, TaskCtx, TaskRef, WorkspaceAt
# from asd.server import ProjectRegistry

# class TaskRegistry(Protocol):
#     def __call__(self, ref: TaskRef) -> Optional[Task]: ...


# def task_registry(project_registry: ProjectRegistry) -> TaskRegistry:
#     def get(ref: TaskRef) -> Optional[Task]:
#         project = project_registry(ref.project)
#         if not project:
#             return None
#         module = project.get(ref.module)
#         if not module:
#             return None
#         return module.get(ref.task)
#     return get

# TaskResults = NewType("TaskResults", MappingProxyType[TaskRef, Hashable])


# class TaskRunner(Protocol):
#     async def __call__(self, tasks: Set[TaskRef]) -> TaskResults:
#         ...


# def task_runner(registry: TaskRegistry, workspace_at: WorkspaceAt) -> TaskRunner:

#     plan: dict[TaskRef, Task] = {}
#     promises: dict[TaskRef,Promise[tuple[TaskRef,Hashable]]] = {}

#     def collect(task_ref: TaskRef, trace: list[TaskRef]) -> None:
#         if task_ref in trace:
#             trace_str = "->\n".join([str(r) for r in trace])
#             raise Exception(f"Circular dependency with tasks {trace_str}")
#         task = registry(task_ref)
#         if not task:
#             raise Exception(f"Task {task_ref} doesn't exist")

#         if task_ref not in plan:
#             plan[task_ref] = task
#             new_trace = [task_ref, *trace]
#             for dep in task.deps:
#                 collect(dep, new_trace)

#     def run_task(ref: TaskRef) -> Promise[Tuple[TaskRef, Hashable]]:
#         async def action() -> tuple[TaskRef,Hashable]:
#             task = plan[ref]
#             deps = await asyncio.gather(*[run_task(dep) for dep in task.deps])
#             deps_map = MappingProxyType({dep[0]: dep[1] for dep in deps})
#             return (ref,await plan[ref].action(TaskCtx(
#                 id=ref.task,
#                 module=ref.module,
#                 project=ref.project,
#                 workspace=workspace_at,
#                 deps=deps_map
#             )))
#         if ref not in promises:
#             promises[ref] = asyncio.create_task(action())
#         return promises[ref]

#     async def run(tasks: Set[TaskRef]) -> TaskResults:
#         for ref in tasks:
#             collect(ref, [])
#         results = await asyncio.gather(*[run_task(ref) for ref in tasks])
#         task_results = TaskResults(MappingProxyType({
#             r[0]:r[1] for r in results
#         }))
#         return task_results
#     return run
