"""
Contains functions for CRUD operations for files and directories between local and
Minio to extend the object operations explained here:
https://min.io/docs/minio/linux/developers/python/API.html.
"""

import io
import logging
import os
from pathlib import Path
from typing import BinaryIO

import cv2
import numpy as np
import pandas as pd  # type: ignore
from minio import Minio, S3Error
from urllib3 import BaseHTTPResponse

from anhaltai_commons_minio.bucket_utils import list_paths_in_bucket
from anhaltai_commons_minio.helper_utils import normalize_minio_object_name


def delete_directory(
    minio_client: Minio, bucket_name: str, bucket_directory: str, **kwargs
):
    """Delete a directory in a minio bucket.

    Args:
      minio_client (Minio): Minio client
      bucket_name (str): Minio bucket name
      bucket_directory (str): directory to delete inside the Minio bucket
    """
    if directory_exists(
        minio_client,
        bucket_name,
        bucket_directory,
    ):
        paths = list_paths_in_bucket(minio_client, bucket_name, bucket_directory)
        for path in paths:
            remove_object(minio_client, bucket_name, path, **kwargs)


def upload_directory(
    minio_client: Minio,
    bucket_name: str,
    local_directory: str,
    remote_directory: str,
    overwrite: bool = False,
):
    """Upload a local directory to Minio.

    Args:
      minio_client (Minio): Minio client
      bucket_name (str): Minio bucket name
      local_directory (str): local path
      remote_directory (str): path inside Minio bucket
      overwrite (bool): If the directory should be overwritten  (Default value = False)
    """

    for dir_path, _, filenames in os.walk(str(Path(local_directory))):
        for filename in filenames:
            local_path = Path(dir_path) / filename

            # Calculate the relative path to maintain the directory structure
            relative_path: Path = local_path.relative_to(local_directory)

            # Create remote path and ensure it's URL compatible
            remote_path: Path = Path(remote_directory) / relative_path

            upload_object_file(
                minio_client=minio_client,
                bucket_name=bucket_name,
                file_path=str(local_path),
                object_name=normalize_minio_object_name(remote_path),
                overwrite=overwrite,
            )


def download_directory(
    minio_client: Minio,
    bucket_name: str,
    remote_directory: str,
    local_directory: str,
    overwrite=False,
):
    """Download a directory from minio to local path

    Args:
      minio_client (Minio): Minio client
      bucket_name (str): Minio bucket name
      remote_directory (str): path inside Minio bucket
      local_directory (str): local path
      overwrite (bool): overwrite existing directory (Default value = False)
    """
    remote_files: list[str] = list_paths_in_bucket(
        minio_client, bucket_name, prefix=normalize_minio_object_name(remote_directory)
    )
    for remote_path in remote_files:
        # Construct local file path
        local_path = normalize_minio_object_name(Path(local_directory, remote_path))
        # Download the file
        download_object_file(
            minio_client, bucket_name, remote_path, local_path, overwrite
        )


def copy_directory_from_bucket_to_bucket(
    origin_minio_client: Minio,
    origin_minio_bucket: str,
    origin_path: str,
    target_minio_client: Minio,
    target_minio_bucket: str,
    target_path: str,
    overwrite=True,
):
    """Copy an object from one bucket to another where origin and target minio
    clients can be different or the same.

    Args:
      origin_minio_client (Minio): Minio client to copy from
      origin_minio_bucket (str): Minio bucket to copy from
      origin_path (str): Path prefix inside the bucket where to copy from
      target_minio_client (str): Minio client to copy to
      target_minio_bucket (str): Minio bucket to copy to
      target_path (str): Path prefix inside the bucket where to copy to
      overwrite (bool): If True, overwrite existing files if they exist (Default
      value = True)

    """

    origin_files: list[str] = list_paths_in_bucket(
        origin_minio_client,
        origin_minio_bucket,
        prefix=normalize_minio_object_name(origin_path),
    )
    for origin_file_path in origin_files:
        # Construct remote file path
        relative_path: Path = Path(origin_file_path).relative_to(Path(origin_path))

        # Create the target file path and ensure it's URL compatible
        target_file_path: Path = Path(target_path) / relative_path

        copy_file_from_bucket_to_bucket(
            origin_minio_client,
            origin_minio_bucket,
            normalize_minio_object_name(origin_file_path),
            target_minio_client,
            target_minio_bucket,
            normalize_minio_object_name(target_file_path),
            overwrite=overwrite,
        )


def copy_path(
    minio_client: Minio,
    bucket_name: str,
    source_path: str,
    dest_path: str,
    overwrite: bool = True,
):
    """Copy all objects from the given source location to the given destination
    location of one minio client.

    Args:
      minio_client (Minio): The MinIO client that is ued to perform all MinIO requests.
      bucket_name (str): The name of the bucket.
      source_path (str): The prefix of source objects.
      dest_path (str): The destination prefix.
      overwrite (bool): If True, overwrite existing files if they exist (
      Default value = True).
    """

    copy_directory_from_bucket_to_bucket(
        origin_minio_client=minio_client,
        origin_minio_bucket=bucket_name,
        origin_path=source_path,
        target_minio_client=minio_client,
        target_minio_bucket=bucket_name,
        target_path=dest_path,
        overwrite=overwrite,
    )


def object_exists(
    minio_client: Minio, bucket_name: str, object_name: str, **kwargs
) -> bool:
    """Check if an object exists in the bucket.

    Args:
      minio_client (Minio): Minio client instance
      bucket_name (str): Minio bucket name
      object_name (str): path inside the bucket

    Returns:
      bool: If the object exists
    """
    object_name = normalize_minio_object_name(object_name)
    try:
        _ = minio_client.stat_object(bucket_name, object_name, **kwargs)
        return True
    except S3Error as error:
        if error.code == "NoSuchKey":
            return False
    return False


def directory_exists(
    minio_client: Minio,
    bucket_name: str,
    directory_path: str,
) -> bool:
    """Checks if the directory exists ( different to object_prefix_exists)

    Args:
      minio_client (Minio): Minio client
      bucket_name (str): Minio bucket name
      directory_path (str): path inside the bucket

    Returns:
      bool: If the directory exists
    """
    directory_path = normalize_minio_object_name(directory_path)

    object_paths: list[str] = list_paths_in_bucket(
        minio_client=minio_client, bucket_name=bucket_name, prefix=directory_path
    )
    if len(object_paths) == 0:
        # In Minio a directory cannot exist without a file
        return False
    if len(object_paths) == 1 and object_paths[0] == directory_path:
        return False
    return True


def object_prefix_exists(
    minio_client: Minio, bucket_name: str, object_prefix: str
) -> bool:
    """Check if an object name (path) prefix exists in the bucket.

    Args:
      minio_client (Minio): Minio client instance
      bucket_name (str): Minio bucket name
      object_prefix (str): path inside the bucket
    Returns:
      bool: If the object prefix exists
    """
    object_prefix = normalize_minio_object_name(object_prefix)
    try:
        _ = next(minio_client.list_objects(bucket_name, prefix=object_prefix))
        return True
    except StopIteration:
        return False


def download_object(
    minio_client: Minio, bucket_name: str, object_name: str, **kwargs
) -> BaseHTTPResponse:
    """Download an object from the bucket.

    Args:
      minio_client (Minio): Minio client instance
      bucket_name (str): Minio bucket name
      object_name (str): path inside the bucket

    Returns:
      BaseHTTPResponse: response of the HTTP request

    """
    object_name = normalize_minio_object_name(object_name)
    logging.debug("Downloading: %s", object_name)
    return minio_client.get_object(
        bucket_name=bucket_name, object_name=object_name, **kwargs
    )


def download_object_file(
    minio_client: Minio,
    bucket_name: str,
    object_name: str,
    file_path: str,
    overwrite=True,
    **kwargs,
) -> bool:
    """Download an object from the bucket and write it to a file.

    Args:
      minio_client (Minio): Minio client instance
      bucket_name (str): Minio bucket name
      object_name (str): path inside the bucket
      file_path (str): local path
      overwrite (bool): If the local existing file should be overwritten (Default
      value = True)

    Returns:
      bool: If the local file was downloaded successfully
    """
    object_name = normalize_minio_object_name(object_name)
    if os.path.isfile(file_path) and not overwrite:
        return False

    logging.debug("Downloading: %s to %s", object_name, file_path)
    minio_client.fget_object(
        bucket_name=bucket_name, object_name=object_name, file_path=file_path, **kwargs
    )
    return True


def download_object_bytes(
    minio_client: Minio, bucket_name: str, object_name: str, **kwargs
) -> io.BytesIO:
    """
    Download an object from the bucket as byte stream.
    Args:
        minio_client (Minio): Minio client
        bucket_name (str): Minio bucket name
        object_name (str): path inside the Minio bucket

    Returns:
        io.BytesIO: object as bytestream
    """

    object_name = normalize_minio_object_name(object_name)
    response: BaseHTTPResponse = download_object(
        minio_client=minio_client,
        bucket_name=bucket_name,
        object_name=object_name,
        **kwargs,
    )
    return io.BytesIO(response.read())


def upload_object_file(
    minio_client: Minio,
    bucket_name: str,
    object_name: str,
    file_path: str,
    overwrite: bool = True,
    **kwargs,
) -> bool:
    """Upload an object from a local file to the bucket.

    Args:
      minio_client (Minio): Minio client instance
      bucket_name (str): Minio bucket name
      object_name (str): path inside the bucket
      file_path (str): local path
      overwrite (bool): If the existing file inside the bucket should be overwritten
      (Default value = True).

    Returns:
      bool: If the local file was successfully uploaded
    """
    object_name = normalize_minio_object_name(object_name)
    already_exists = object_exists(minio_client, bucket_name, object_name)
    if overwrite or not already_exists:
        logging.debug("Uploading: %s to Minio: %s", file_path, object_name)
        minio_client.fput_object(
            bucket_name, object_name, os.path.join(file_path), **kwargs
        )
        return True

    if already_exists:
        logging.debug("Already exists: %s", object_name)

    return False


def upload_object_bytes(
    minio_client: Minio,
    bucket_name: str,
    object_name: str,
    data_bytes: BinaryIO,
    data_length: int = -1,
    overwrite: bool = True,
    content_type: str = "application/octet-stream",
    **kwargs,
) -> bool:
    """Upload an object from a byte stream to the bucket.

    Args:
      minio_client (Minio): Minio client instance
      bucket_name (str): Minio bucket name
      object_name (str): path inside the bucket
      data_bytes (BinaryIO): byte stream as BinaryIO instance
      data_length (int): length of the byte stream (Default value = -1).
      overwrite (bool): If the existing file inside the bucket should be overwritten
      content_type: Content type of the object.
      (Default value = True).

    Returns:
      bool: If the object was uploaded successfully

    """
    object_name = normalize_minio_object_name(object_name)
    if object_exists(minio_client, bucket_name, object_name) and not overwrite:
        return False

    logging.debug("Uploading binary data to Minio: %s", object_name)
    minio_client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=data_bytes,
        length=data_length,
        content_type=content_type,
        **kwargs,
    )

    return True


def remove_object(
    minio_client: Minio, bucket_name: str, object_name: str, **kwargs
) -> bool:
    """Remove an object from the bucket if it exists.

    Args:
      minio_client (Minio): Minio client instance
      bucket_name (str): Minio bucket name
      object_name (str): path inside the bucket

    Returns:
      bool: If the object was removed

    """
    object_name = normalize_minio_object_name(object_name)
    if object_exists(minio_client, bucket_name, object_name):
        minio_client.remove_object(bucket_name, object_name, **kwargs)
        logging.debug("Deleted: %s", object_name)
        return True

    logging.debug("Skip delete operation. Not existing: %s", object_name)
    return False


def copy_file_from_bucket_to_bucket(
    origin_minio_client: Minio,
    origin_minio_bucket: str,
    origin_path: str,
    target_minio_client: Minio,
    target_minio_bucket: str,
    target_path: str,
    overwrite=True,
    **kwargs,
):
    """Copy an object from one bucket to another where origin and target minio clients
    can be different or the same.

    Args:
      origin_minio_client (Minio): Minio client to copy from
      origin_minio_bucket (str): Minio bucket to copy from
      origin_path (str): Path prefix inside the bucket where to copy from
      target_minio_client (str): Minio client to copy to
      target_minio_bucket (str): Minio bucket to copy to
      target_path (str): Path prefix inside the bucket where to copy to
      overwrite (bool): If True, overwrite existing file if it exists (Default value =
      True)

    Returns:
      bool: If the object was uploaded

    """
    already_exists: bool = object_exists(
        target_minio_client, target_minio_bucket, target_path
    )

    if already_exists and not overwrite:
        return False

    response: BaseHTTPResponse = download_object(
        origin_minio_client, origin_minio_bucket, origin_path, **kwargs
    )
    data_bytes: io.BytesIO = io.BytesIO(response.read())
    if "Content-Length" in response.headers:
        content_length = int(response.headers["Content-Length"])  # get exact length
    else:
        content_length = -1  # use unknown length which can result in less performance

    upload_object_bytes(
        target_minio_client,
        target_minio_bucket,
        target_path,
        data_bytes,
        content_length,
        overwrite=overwrite,
    )

    return True


def download_data_frame(
    minio_client: Minio, bucket_name: str, object_name: str, encoding="utf-8", **kwargs
) -> pd.DataFrame:
    """Download a csv file decoded as pandas dataframe from the bucket.

    Args:
      minio_client (Minio): Minio client
      bucket_name (str): Minio bucket name
      object_name (str): path inside the bucket
      encoding (str): the encoding of the CSV file (Default value = "utf-8")
      kwargs (str): additional keyword arguments to pass to pd.read_csv()

    Returns:
      pd.DataFrame: A pandas DataFrame

    """
    object_name = normalize_minio_object_name(object_name)
    response: BaseHTTPResponse = download_object(
        minio_client, bucket_name, object_name, **kwargs
    )
    data: bytes = response.read()
    string_io: io.StringIO = io.StringIO(data.decode(encoding))
    return pd.read_csv(string_io, *kwargs)


def download_json(
    minio_client: Minio, bucket_name: str, object_name: str, encoding="utf-8", **kwargs
) -> str:
    """Download a JSON file from the bucket decoded as a byte stream.

    Args:
      minio_client (Minio): Minio client
      bucket_name (str): Minio bucket name
      object_name (str): path inside the bucket
      encoding (str): The character encoding used to decode the byte stream
      (Default value = "utf-8")

    Returns:
      str: The contents of the JSON file as a string.

    """
    object_name = normalize_minio_object_name(object_name)
    response: BaseHTTPResponse = download_object(
        minio_client, bucket_name, object_name, **kwargs
    )
    data: bytes = response.read()
    return data.decode(encoding)


def download_image(
    minio_client: Minio, bucket_name: str, object_name: str, **kwargs
) -> np.ndarray:
    """Download an image file as numpy array from the bucket.

    Args:
      minio_client(Minio): Minio client
      bucket_name(str): Minio bucket name
      object_name(str): path inside the bucket

    Returns:
      np.ndarray: image as a numpy array

    """
    object_name = normalize_minio_object_name(object_name)
    response: BaseHTTPResponse = download_object(
        minio_client, bucket_name, object_name, **kwargs
    )
    data: bytes = response.read()
    buffer: np.ndarray = np.frombuffer(data, np.uint8)
    return cv2.imdecode(buffer, cv2.IMREAD_COLOR).astype(np.uint8)
