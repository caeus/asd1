# import os
# import runpy
# from types import MappingProxyType
# from typing import Any, Final, Optional, Protocol, TypeGuard

# from asd.api import ModuleCtx, ModuleId, ProjectId, Task, TaskId, WorkspaceAt
# from asd.kernel import PROJECT_MARKER












    

    



# class ProjectRegistry(Protocol):
#     def __call__(self, id: ProjectId) -> Optional[Project]: ...


# def project_registry(loader:ProjectLoader) -> ProjectRegistry:
#     projects:dict[ProjectId,Optional[Project]] = {} 
#     def get(id: ProjectId) -> Optional[Project]:
#         if id in projects:
#             return projects[id]
#         project=loader(id)
#         projects[id]=project
#         return project
#     return get








