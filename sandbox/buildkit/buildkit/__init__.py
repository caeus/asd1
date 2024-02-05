


from typing import Hashable
from asd.dls import ModuleCtx, TaskCtx


def my_common_config(ctx:ModuleCtx)->None:
    @ctx.task()
    async def common(ctx:TaskCtx)->Hashable:
        print("Works?")