

from typing import Hashable
from asd.dls import ModuleCtx, TaskCtx, project
from buildkit import my_common_config

@project
def root(ctx: ModuleCtx) -> None:
    my_common_config(ctx)
    
    @ctx.task()
    async def dummy(ctx: TaskCtx) -> Hashable:
        print("alkdsjlaskjdlksaj")
        ...
