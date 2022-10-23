import pathlib
import uuid

from hidori_common.dirs import get_cache_home


def get_pipelines_path() -> pathlib.Path:
    return get_cache_home() / "pipelines"


def create_pipeline_dir(target_id: str) -> pathlib.Path:
    dirname = f"hidori-{uuid.uuid4().hex}"
    path = get_pipelines_path() / target_id / dirname
    path.mkdir(parents=True, exist_ok=False)
    return path
