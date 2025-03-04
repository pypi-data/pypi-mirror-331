"""pydev program"""

import sys
import click
import shutil
import logging

from . import utils
from . import messages

logger = logging.getLogger()


@click.group(chain=True)
def main():
    pass


@main.command
def info():
    """Project info including pypi versions"""
    name = utils.get_config("project.name")
    version = utils.get_config("project.version")
    project_root = utils.get_project_root()
    releases = utils.pypi_releases(name)
    print("name", name)
    print("version", version)
    print("location", project_root)
    print("pypi.releases", releases)


@main.command
def clean():
    """Delete build and dist folders"""
    project_root = utils.get_project_root(strict=True)
    folders = "build", "dist"

    for folder in folders:
        path = project_root.joinpath(folder)
        if path.is_dir():
            print(f"rmtree {folder}")
            shutil.rmtree(path)


@main.command
@click.option("-y", "--yes", is_flag=True)
def prune(yes):
    """Delete all runtime folders"""
    project_root = utils.get_project_root(strict=True)
    folders = "build", "dist", ".venv", ".nox", ".tox"

    folders = [f for f in folders if project_root.joinpath(f).exists()]

    confirm = yes or utils.confirm_choice(
        f"Do you want to delete runtime folders {folders}"
    )
    if not confirm:
        exit(1)

    for folder in folders:
        path = project_root.joinpath(folder)
        if path.is_dir():
            print(f"rmtree {folder}")
            shutil.rmtree(path)


@main.command
def bump():
    """Bump static version in pyproject.toml"""
    utils.bump_version()


@main.command
def build():
    """Build project wheel"""
    utils.build_project()


@main.command
def dump():
    """Dump wheel and sdist contents"""
    project_root = utils.get_project_root()
    dist = project_root.joinpath("dist")

    for file in dist.glob("*.whl"):
        utils.run_command(f"unzip -l {file}")

    for file in dist.glob("*.tar.gz"):
        utils.run_command(f"tar -ztvf {file}")


@main.command
@click.option("-t", "--test-pypi", is_flag=True)
@click.option("-v", "--verbose", is_flag=True)
def publish(test_pypi=False, verbose=False):
    """Publish project with twine"""

    if not utils.get_config("tool.pydev.allow-publish"):
        print(messages.ALLOW_PUBLISH)
        exit(1)

    utils.build_project(clean=True, auto_bump=True)

    python = sys.executable

    flags = ""
    if test_pypi:
        flags += " --repository testpypi"
    if verbose:
        flags += " --verbose"

    command = f"{python} -mtwine upload {flags} dist/*"

    utils.run_command(command)
