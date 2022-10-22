import os
import pathlib
import platform
import uuid


def get_cache_home() -> pathlib.Path:
    if platform.system() != "Linux":
        # TODO: Support for macos and windows
        raise NotImplementedError("Unsupported System")

    home_path = pathlib.Path(os.environ.get("XDG_CACHE_HOME", "~/.cache"))
    if home_path.exists():
        return pathlib.Path.expanduser(home_path / "hidori")
    else:
        raise RuntimeError("cache home directory does not exist or path is invalid")


def get_pipelines_path() -> pathlib.Path:
    return get_cache_home() / "pipelines"


def create_pipeline_dir(target_id: str) -> pathlib.Path:
    dirname = f"hidori-{uuid.uuid4().hex}"
    path = get_pipelines_path() / target_id / dirname
    path.mkdir(parents=True, exist_ok=False)
    return path
