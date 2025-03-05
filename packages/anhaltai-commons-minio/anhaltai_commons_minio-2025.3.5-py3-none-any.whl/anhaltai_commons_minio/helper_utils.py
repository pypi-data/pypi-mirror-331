"""
Contains functions that are used commonly in commons-minio
"""

import re
from pathlib import Path, PurePath

from minio.helpers import check_object_name


def normalize_minio_object_name(path: str | Path) -> str:
    """
    Convert path to be compatible for Minio.
    Further documentation:
    - https://min.io/docs/minio/linux/operations/concepts/thresholds.html#id4
    - https://github.com/minio/minio-py/blob/master/minio/helpers.py at
    check_object_name
    Args:
        path (str | Path):

    Returns:
        str: path as string in POSIX style compatible to Minio
    """

    # force forward slashes compatible for each os (os and pathlib cannot solve this)
    path_str: str = str(path).replace("\\", "/").strip()
    posix_path: str = PurePath(path_str).as_posix()

    # path containing only dots e.g. "." are not allowed
    if not path_str or re.fullmatch(r"[./]*", path_str):
        return ""

    check_object_name(posix_path)  # check by minio function must not fail
    return posix_path
