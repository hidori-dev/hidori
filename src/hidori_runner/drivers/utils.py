import pathlib

from hidori_common.dirs import get_cache_home


def get_pipelines_path() -> pathlib.Path:
    return get_cache_home() / "pipelines"


def get_calls_path() -> pathlib.Path:
    return get_cache_home() / "calls"


def create_pipeline_dir(exchange_id: str, target_id: str) -> pathlib.Path:
    dirname = f"hidori-{exchange_id}"
    path = get_pipelines_path() / target_id / dirname
    path.mkdir(parents=True, exist_ok=False)
    return path


def create_call_dir(exchange_id: str, target_id: str) -> pathlib.Path:
    dirname = f"hidori-{exchange_id}"
    path = get_calls_path() / target_id / dirname
    path.mkdir(parents=True, exist_ok=False)
    return path
