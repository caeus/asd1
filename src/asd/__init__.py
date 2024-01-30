from asd.server import ASD_OBJECT_MARKER, ASDModuleConfig, ModuleConfig, is_asd_module_config

from asd.api import *


def project(configure: ModuleConfig) -> ASDModuleConfig:
    setattr(configure, ASD_OBJECT_MARKER, "project")
    if is_asd_module_config(configure):
        return configure
    raise Exception("This won't ever happen, but beware...")
