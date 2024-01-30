


from typing import Hashable
from asd import ModuleCtx, TaskCtx, project

@project
def root(ctx:ModuleCtx)->None: 
    @ctx.task()
    def dummy(ctx:TaskCtx)->Hashable:
        ...