
from types import MappingProxyType
from typing import NewType, Protocol, Set
from asd.backend.tasks.repo import TasksRepo

from asd.dsl import Task, TaskRef


TasksPlan = NewType('TasksPlan', MappingProxyType[TaskRef, Task])


class TaskPlanner(Protocol):
    def __call__(self, tasks: Set[TaskRef]) -> TasksPlan: ...


def create_task_planner(repo: TasksRepo) -> TaskPlanner:
    def plan(tasks: Set[TaskRef]) -> TasksPlan:
        collector: dict[TaskRef, Task] = {}
        def collect(task_ref: TaskRef, trace: list[TaskRef]) -> None:
            if task_ref in collector:
                return None
            if task_ref in trace:
                trace_str = "->\n".join([str(r) for r in trace])
                raise Exception(f"Circular dependency with tasks {trace_str}")
            task = repo.get(task_ref)
            if task is None:
                raise Exception(f"Task {task_ref} doesn't exist")

            collector[task_ref] = task
            new_trace = [task_ref, *trace]
            for dep in task.deps:
                collect(dep, new_trace)
        for ref in tasks:
            collect(ref,[])
        return TasksPlan(MappingProxyType(collector))
    return plan
