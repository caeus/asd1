

import os
from asd.api import TaskCtx
from asd.bind import Bind
from asd.cli import CWD, MatchedProjects, MatchedTasks, QueryStr, cli_runner
from .fake_projects import FakeModuleCtx, FakeProjectCtx, FakeProjects, FakeWorkspaceCtx, fake_workspace_module



def test_get_current_path() -> None:
    @fake_workspace_module
    def test_module(ctx:FakeWorkspaceCtx)->None:
        @ctx.project("domains/infrastructure/kit/pg")
        def _(ctx:FakeProjectCtx)->None: 
            @ctx.module
            def root(ctx:FakeModuleCtx)->None:
                @ctx.task()
                async def dummy(ctx:TaskCtx)->None:
                    ...
        @ctx.project("domains/infrastructure/kit/mongo")
        def _(ctx:FakeProjectCtx)->None: ...
        @ctx.project("domains/infrastructure/kit/http")
        def _(ctx:FakeProjectCtx)->None: ...
        @ctx.project("domains/users/lib")
        def _(ctx:FakeProjectCtx)->None: ...
        @ctx.project("domains/users/client")
        def _(ctx:FakeProjectCtx)->None: ...
        @ctx.project("domains/users/app")
        def _(ctx:FakeProjectCtx)->None: ...
        

    @Bind.module
    def input_module(bind:Bind)->None:
        bind.value(CWD,CWD(os.path.join(os.getcwd(),"sandbox","subdomain2","project21")))
        bind.value(QueryStr,QueryStr('domains/infras*/**:root:dummy'))

    @cli_runner(Bind.merge(test_module,input_module))
    def _(matched_tasks:MatchedTasks)->None:
        print(matched_tasks)
        print(matched_tasks)
        print(matched_tasks)
        print(matched_tasks)
        print(matched_tasks)
## Test that venv creation works
## Test that test_running works
## implement test running with async support
## test access of values (inside task action)
## test circular dependencies  
## ergonomics: process running, caching, and sha256ing files      

    
