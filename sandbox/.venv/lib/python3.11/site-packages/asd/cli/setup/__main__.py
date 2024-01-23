

from dataclasses import dataclass
import os
import subprocess
import tomllib
import venv

from asd.core import WORSPACE_MARKER


@dataclass
class WorkspaceInfo:
    root: str
    cwd: str

    @property
    def config_file(self) -> str:
        return os.path.join(self.root, WORSPACE_MARKER)

    @property
    def cwd_path(self) -> str:
        return os.path.join(self.root, self.cwd)


@dataclass
class WorkspaceConfig:
    info: WorkspaceInfo
    venv_at: str
    installs: list[str]

    def __init__(self,
                 info: WorkspaceInfo,
                 /,
                 installs: list[str],
                 venv_at: str = ".venv") -> None:
        self.venv_at = venv_at
        self.info = info
        self.installs = installs

    @property
    def venv_path(self) -> str:
        return os.path.join(self.info.root, self.venv_at)


def find_workspace(cwd: str) -> str:
    current = os.path.abspath(cwd)
    while not os.path.exists(os.path.join(current, WORSPACE_MARKER)):
        parent = os.path.dirname(current)
        if parent == current:
            raise Exception(
                f"Reached root of file system, couldn't find a folder with a {WORSPACE_MARKER} file")
        # print(current)
        current = parent
    return WorkspaceInfo(root=current, cwd=os.path.relpath(current, cwd))


def project_config(info: WorkspaceInfo) -> str:
    with open(info.config_file, "rb") as config_file:
        return WorkspaceConfig(info, **tomllib.load(config_file))


def create_venv(config: WorkspaceConfig) -> None:
    venv.create(config.venv_path,with_pip=True)
    # subprocess.check_call(["python","-m","venv",config.venv_at],cwd=config.info.root)
    # subprocess.check_call(["tree",config.venv_at],cwd=config.info.root)


def install_venv(config: WorkspaceConfig) -> None:
    for install in config.installs:
        subprocess.check_call([
            os.path.join(config.venv_at, "bin", "python"),
            "-m",
            "pip",
            "install",
            install
        ], cwd=config.info.root)

        ...
def run_asd(config: WorkspaceConfig)->None:  
    subprocess.check_call([
            os.path.join(config.venv_path, "bin", "python"),
            "-m",
            "asd.cli.core",
        ], cwd=config.info.cwd_path)


workspace = find_workspace(os.getcwd())
config = project_config(workspace)
create_venv(config)
install_venv(config)
run_asd(config)
