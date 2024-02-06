from injector import Injector
from asd.backend.cli import Cli, create_cli
from asd.backend.tasks.planner import create_task_planner
from asd.backend.tasks.repo import DefaultProjectsRepo, DefaultTasksRepo, create_project_loader
from asd.backend.tasks.runner import create_task_runner_provider
from asd.dsl import get_working_path
from asd.kernel import get_cwd, get_workspace_location
from asd.kernel.bind import Bind, ConfigureModule


@Bind.module
def launcher_module(bind: Bind) -> None:
    bind.singleton(create_cli)
    bind.singleton(DefaultTasksRepo.create)
    bind.singleton(DefaultTasksRepo.create)
    bind.singleton(DefaultProjectsRepo.create)
    bind.singleton(create_project_loader)
    bind.singleton(get_workspace_location)
    bind.singleton(get_cwd)
    bind.singleton(get_working_path)
    bind.singleton(create_task_planner)
    bind.singleton(create_task_runner_provider)
    ...


def application(override: list[ConfigureModule] = []) -> Cli:
    injector = Injector([launcher_module, *override], auto_bind=False)
    return injector.get(Cli)


def main() -> None:
    application()()
