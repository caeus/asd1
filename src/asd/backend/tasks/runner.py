

import asyncio
from asyncio import Task as Promise
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final, Hashable, Never, Protocol, Tuple

import click

from asd.backend.tasks.planner import TasksPlan
from asd.dsl import TaskCtx, TaskRef
from asd.kernel import WorkspaceAt


@dataclass(frozen=True)
class Succ[T]:
    value: Final[T]
    def get(self)->T:
        return self.value


@dataclass(frozen=True)
class Err:
    value: Final[Exception]
    def get(self)->Never:
        raise self.value


type Result[T] = Succ[T] | Err


class TaskRunner(Protocol):
    async def __call__(
        self, plan: TasksPlan) -> MappingProxyType[TaskRef, Hashable]: ...


class TaskRunnerProvider(Protocol):
    def __call__(self) -> TaskRunner: ...


def create_task_runner_provider(workspace_at: WorkspaceAt) -> TaskRunnerProvider:
    def provide() -> TaskRunner:
        async def run(plan: TasksPlan) -> MappingProxyType[TaskRef, Hashable]:
            promises: dict[TaskRef, Promise[tuple[TaskRef, Hashable]]] = {}

            def run_task(ref: TaskRef) -> Promise[Tuple[TaskRef, Hashable]]:
                async def action() -> tuple[TaskRef, Hashable]:
                    task = plan[ref]
                    deps = await asyncio.gather(*[run_task(dep) for dep in task.deps])
                    deps_map = MappingProxyType(
                        {dep[0]: dep[1] for dep in deps})
                    try:
                        res = await plan[ref].action(TaskCtx(
                            id=ref.task,
                            module=ref.module,
                            project=ref.project,
                            workspace=workspace_at,
                            deps=deps_map
                        ))
                        return (ref, res)
                    except Exception as e:
                        click.echo(
                            f"Task {ref} failed with error {e}",
                            err=True)
                        raise e
                if ref not in promises:
                    promises[ref] = asyncio.create_task(action())
                return promises[ref]

            async def run_task_safely(ref: TaskRef) -> tuple[TaskRef,Result[Hashable]]:
                try:
                    return ref,Succ(await run_task(ref))
                except Exception as exp:
                    return ref, Err(exp)
            results_list: list[Tuple[TaskRef, Result[Hashable]]] = await asyncio.gather(*[run_task_safely(ref) for ref in plan])
            return MappingProxyType({
                ref: result.get()
                for (ref, result) in results_list
            })
        return run
    return provide
