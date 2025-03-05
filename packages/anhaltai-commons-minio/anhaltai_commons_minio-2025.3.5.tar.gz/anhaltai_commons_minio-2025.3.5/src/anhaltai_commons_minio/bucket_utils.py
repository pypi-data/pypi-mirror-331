"""
Contains functions for operations with Minio buckets to extend the bucket operations
explained here: https://min.io/docs/minio/linux/developers/python/API.html.
"""

import logging
from collections import defaultdict
from pathlib import Path
from typing import List, DefaultDict

from minio import Minio

from anhaltai_commons_minio.helper_utils import normalize_minio_object_name


def list_paths_in_bucket_in_directory(
    minio_client: Minio, bucket_name: str, dir_path: str = "", **kwargs
) -> list[str]:
    """
    Lists all paths of a bucket inside the directory specified by dir_path.

    Args:
      minio_client: Minio client
      bucket_name: Minio bucket name
      dir_path: Directory path where files are located

    Returns:
      list[str]: List of all found paths. Returns empty list if no files and
      directories have been found
    """

    dir_path = normalize_minio_object_name(dir_path)
    file_paths: list[str] = list_paths_in_bucket(
        minio_client=minio_client, bucket_name=bucket_name, prefix=dir_path, **kwargs
    )

    filtered_file_paths = [
        file_path for file_path in file_paths if file_path.startswith(dir_path + "/")
    ]

    return filtered_file_paths


def list_paths_in_bucket(
    minio_client: Minio, bucket_name: str, prefix: str = "", **kwargs
) -> list[str]:
    """Get all already existing paths of a bucket that have the given prefix by using
    only one request instead of one for each file.
    This function simplifies the function list_objects by returning only the object
    names (paths).
    It is still an expensive function call because all objects within the bucket are
    iterated.

    Args:
      minio_client: Minio client
      bucket_name: Minio bucket name
      prefix: Get only paths that start with this prefix

    Returns:
      list[str]: List of all found paths. Returns empty list if no files and
      directories have been found
    """

    logging.debug("Getting existing paths from Minio bucket %s", bucket_name)
    minio_objects: List = minio_client.list_objects(
        bucket_name=bucket_name,
        recursive=True,
        prefix=normalize_minio_object_name(prefix),
        **kwargs,
    )
    return [item.object_name for item in minio_objects]


def count_file_endings_in_bucket(
    minio_client: Minio,
    bucket_name: str,
    prefix: str = "",
    file_endings: list[str] | None = None,
) -> dict:
    """Count the number of files (with given prefix) in a bucket by their extensions.
    Optional they are count by the listed file extensions and/or file endings.

    Args:
      minio_client (Minio): Minio client
      bucket_name (str): Minio bucket name
      prefix (str): Get only paths that start with this prefix (Default value = "")
      file_endings (list[str] | None): List of file extensions and endings e.g. [
      ".png", ".jpg", "labels.txt"] that should be count. If the value is None all
      the files are count by all the found file extensions (Default value = None)

    Returns:
      dict: Keys represent file extensions and endings, while the values indicate their
      quantities.

    """

    count_dict: DefaultDict[str, int] = defaultdict(int)
    file_paths: list[str] = list_paths_in_bucket(
        minio_client=minio_client, bucket_name=bucket_name, prefix=prefix
    )

    if file_endings:
        for ext in file_endings:
            count_dict[ext] = 0  # Ensure all specified endings are initialized

        for path in file_paths:
            for ext in file_endings:
                if path.endswith(ext):
                    count_dict[ext] += 1
    else:
        for path in file_paths:
            ext = Path(path).suffix
            count_dict[ext] += 1

    return dict(count_dict)
