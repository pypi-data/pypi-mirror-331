"""pydev legacy methods"""

import os

from pathlib import Path


def system_python(version=None):
    """Python in the system path"""
    if not version:
        version = "3"

    path = os.getenv("PATH", "/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin")
    path = path.split(os.pathsep)

    pattern = "python" + version
    items = [i for p in path for i in Path(p).glob(pattern)]

    return next(items, None)


def pyenv_versions():
    """pyenv versions"""

    pyenv_root = os.getenv("PYENV_ROOT", "~/.pyenv")
    pyenv_root = Path(pyenv_root).expanduser()

    return pyenv_root.glob("versions/*")


def pyenv_python(version: str = None) -> Path:
    """pyenv binary for version prefix"""

    if not version:
        version = "3.*"
    elif version.count(".") < 2:
        version += ".*"

    pyenv_root = os.getenv("PYENV_ROOT", "~/.pyenv")
    pyenv_root = Path(pyenv_root).expanduser()

    if not pyenv_root.exists():
        return None

    pattern = f"versions/{version}/bin/python"

    return next(pyenv_root.glob(pattern), None)


def conda_envs():
    """conda environments"""

    conda_root = os.getenv("CONDA_PREFIX", "~/miniconda3")
    conda_root = Path(conda_root).expanduser()

    return [p for p in conda_root.glob("envs/*") if p.joinpath("bin/python").exists()]


def conda_python(name: str = None) -> Path:
    """conda binary for named env"""

    conda_root = os.getenv("CONDA_PREFIX", "~/miniconda3")
    conda_root = Path(conda_root).expanduser()

    if name:
        conda_env = conda_root.joinpath(f"envs/{name}")
    else:
        conda_env = conda_root

    if conda_env.exists():
        return conda_env.joinpath("bin/python")


def which_python(version=None, target=None):
    """Locate python matching version/target"""
    if target == "pyenv":
        return pyenv_python(version)

    if target == "conda":
        return conda_python(version)

    if target in ("system", None):
        return system_python(version)
