from typing import Protocol
from asd.backend.tasks.planner import TaskPlanner
from asd.backend.tasks.repo import TasksRepo
from asd.backend.tasks.runner import TaskRunnerProvider

from asd.kernel import RunCmd


class TasksService(Protocol):
    async def __call__(self, cmd: RunCmd) -> None: ...


def create_tasks_service(
        repo: TasksRepo,
    planner: TaskPlanner,
        runner_provider: TaskRunnerProvider) -> TasksService:
    async def service(cmd: RunCmd) -> None:
        tasks = repo.query(cmd.tasks)
        if len(tasks) == 0:
            raise Exception(f"Query {cmd.tasks} didn't match any task")
        plan = planner(tasks)
        runner=runner_provider()
        await runner(plan)
    return service
