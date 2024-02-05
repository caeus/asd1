

# import os

# from asd.api import TaskCtx
# from asd.bind import Bind
# from asd.cli import CWD, MatchedTasks, QueryStr, cli_runner
# from asd.runner import TaskRunner
# from asd.workspace.config import WorkspaceConfig
# from .projects_test import FakeModuleCtx, MockProjectCtx, MockWorkspaceCtx, mock_workspace_module


# @mock_workspace_module
# def mock_project(ctx: MockWorkspaceCtx) -> None:
#     @ctx.project("domains/infrastructure/kit/pg")
#     def _(ctx: MockProjectCtx) -> None:
#         @ctx.module
#         def root(ctx: FakeModuleCtx) -> None:
#             @ctx.task()
#             async def dummy(ctx: TaskCtx) -> str:
#                 return "HOLA"

#     @ctx.project("domains/infrastructure/kit/mongo")
#     def _(ctx: MockProjectCtx) -> None: ...
#     @ctx.project("domains/infrastructure/kit/http")
#     def _(ctx: MockProjectCtx) -> None: ...
#     @ctx.project("domains/users/lib")
#     def _(ctx: MockProjectCtx) -> None: ...
#     @ctx.project("domains/users/client")
#     def _(ctx: MockProjectCtx) -> None: ...
#     @ctx.project("domains/users/app")
#     def _(ctx: MockProjectCtx) -> None: ...


# def test_get_current_path() -> None:

#     @Bind.module
#     def input_module(bind: Bind) -> None:
#         bind.value(CWD,
#                    CWD(
#                        os.path.join(os.getcwd(),
#                                     "sandbox",
#                                     "subdomain2",
#                                     "project21")
#                    ))
#         bind.value(QueryStr, QueryStr('domains/infras*/**:root:dummy'))

#     @cli_runner(input_module)
#     async def _(matched_tasks: MatchedTasks,
#                 task_runner: TaskRunner,
#                 config:WorkspaceConfig) -> None:
#         sss = await task_runner(matched_tasks)
#         print(sss)

# # Test that venv creation works
# # Test that test_running works
# # implement test running with async support
# # test access of values (inside task action)
# # test circular dependencies
# # ergonomics: process running, caching, and sha256ing files
