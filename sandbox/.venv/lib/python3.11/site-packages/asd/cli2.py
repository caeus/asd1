
import glob
import os

import click

from asd.core import PACKAGE_MARKER, TaskRef, TaskRunner, Workspace, WorkspaceRoot


def _parse_ref(raw_ref: str, workspace_path: str,
               package_path: str, ) -> list[TaskRef]:
    colons = raw_ref.count(":")
    if colons > 2 or colons < 1:
        raise Exception(f"wrong ref format `{raw_ref}`")
    if colons == 2:
        parts = raw_ref.split(":")
        package_glob = parts[0]
        project = parts[1]
        target = parts[2]
        packages = glob.glob(os.path.join(
            package_glob, PACKAGE_MARKER), root_dir=workspace_path, recursive=True)

        return [TaskRef(package=os.path.dirname(fabricpy), project=project, task=target) for fabricpy in packages]
    if colons == 1:
        parts = raw_ref.split(":")
        project = parts[0]
        target = parts[1]
        return [TaskRef(package=package_path, project=project, task=target)]
    raise Exception("This will never happen")


def app() -> None:
    @click.command(context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True
    ))
    @click.argument('ref', type=str)
    def run(ref: str) -> None:
        workspace_path = WorkspaceRoot(os.environ["WORKSPACE_PATH"])
        package_path = os.environ["PACKAGE_PATH"]
        workspace = Workspace.at(workspace_path)
        runner = TaskRunner(workspace)
        targets: list[TaskRef] = []
        parsed_refs = _parse_ref(ref, workspace_path=workspace_path,
                                 package_path=package_path)
        for ref in parsed_refs:
            if ref in runner:
                targets.append(ref)
        if len(targets) == 0:
            raise Exception(f"target refs `{str}` didn't match any target")
        for ref in targets:
            runner.run(ref)

    return run


def run() -> None:
    app()()
