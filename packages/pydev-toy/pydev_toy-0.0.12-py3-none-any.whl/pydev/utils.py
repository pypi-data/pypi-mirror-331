"""pydev utils"""

import os
import re
import sys
import json
import tomli
import shutil
import semver
import subprocess

from pathlib import Path

from functools import lru_cache

from packaging.version import Version

from urllib import request
from urllib.error import HTTPError


@lru_cache
def get_project_root(strict=False):
    """Walk up to find pyproject.toml"""

    cwd = Path.cwd()

    for path in cwd, *cwd.parents:
        if path.joinpath("pyproject.toml").exists():
            return path

    if strict:
        raise FileNotFoundError("pyproject.toml")


def run_command(command, echo=True, strict=False, chgdir=True):
    """Run shell command"""

    if echo:
        print(command)

    cwd = None
    if chgdir:
        cwd = get_project_root()
        if cwd is None:
            print("pyproject.toml file not found!")
            exit(1)

    rc = subprocess.run(command, cwd=cwd, shell=True)

    if strict and rc != 0:
        raise RuntimeError("Command failed!")


@lru_cache
def load_config():
    """Load pyproject.toml file"""

    pyproject = Path("pyproject.toml").resolve(strict=True)

    with pyproject.open("rb") as f:
        return tomli.load(f)


def get_config(item: str):
    """Query pyproject.toml file"""

    data = load_config()

    for i in item.split("."):
        data = data.get(i, None)
        if data is None:
            break

    return data


def search_path(pattern: str, path=None):
    """Search items in path"""

    if path is None:
        path = os.getenv("PATH")
    if isinstance(path, str):
        path = path.split(os.pathsep)
    if isinstance(path, os.PathLike):
        path = [path]

    for p in path:
        p = Path(p)
        yield from p.glob(pattern)


def confirm_choice(message, default: bool = None):
    prompt = f"{message} (yes/no):"

    while True:
        user_input = input(prompt)
        if user_input.lower() in ("y", "yes"):
            return True
        if user_input.lower() in ("n", "no"):
            return False
        if user_input == "" and default is not None:
            return default


def pypi_releases(name):
    """List of version on pypi"""
    url = f"https://pypi.org/pypi/{name}/json"
    try:
        res = request.urlopen(url)
        data = json.load(res)
        releases = data.get("releases", [])
        return sorted(releases, key=Version, reverse=True)
    except HTTPError:
        return []


def bump_version():
    """Bump patch version in pyproject"""
    project_root = get_project_root()
    pyproject = project_root.joinpath("pyproject.toml").resolve(strict=True)
    buffer = pyproject.read_text()
    pattern = re.compile(
        r'^version \s* = \s* "(.+)" \s*', flags=re.VERBOSE | re.MULTILINE
    )
    if match := pattern.search(buffer):
        version = semver.VersionInfo.parse(match.group(1))
    else:
        raise ValueError("Could not find version setting")
    new_version = version.bump_patch()
    print(f"Updating version to {new_version} ...")
    output = pattern.sub(f'version = "{new_version}"\n', buffer)
    pyproject.write_text(output)


def already_released():
    name = get_config("project.name")
    version = get_config("project.version")
    releases = pypi_releases(name)
    return version in releases


def build_project(*, clean=False, auto_bump=False):
    """Build project wheel"""

    # bump version if needed
    if auto_bump and already_released():
        bump_version()

    python = sys.executable
    project_root = get_project_root(strict=True)
    dist = project_root.joinpath("dist")

    # clean dist folder if present
    if clean and dist.is_dir():
        print(f"rmtree {dist}")
        shutil.rmtree(dist)

    # pick target depending on setup config
    if project_root.joinpath("setup.py").exists():
        target = "sdist"
    else:
        target = "wheel"

    run_command(f"{python} -m build --{target}")
