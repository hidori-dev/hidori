import os
import pathlib
import platform


def get_user_cache_path() -> pathlib.Path:
    if platform.system() != "Linux":
        # TODO: Support for macos and windows
        raise NotImplementedError("Unsupported System")

    return pathlib.Path.expanduser(
        pathlib.Path(os.environ.get("XDG_CACHE_HOME", "~/.cache"))
    )


def get_cache_home() -> pathlib.Path:
    home_path = get_user_cache_path()
    if home_path.exists():
        return pathlib.Path.expanduser(home_path / "hidori")
    else:
        raise RuntimeError("cache home directory does not exist or path is invalid")


def get_tmp_home() -> pathlib.Path:
    if platform.system() != "Linux":
        # TODO: Support for macos and windows
        raise NotImplementedError("Unsupported System")

    tmp_path = pathlib.Path("/tmp")
    if tmp_path.exists():
        return tmp_path
    else:
        raise RuntimeError("tmp home directory does not exist or path is invalid")
