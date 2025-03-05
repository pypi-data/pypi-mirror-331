"""
Contains a custom subclass of NextCloud to implement needed behavior to upload and
download files locally in connection with Minio.
"""

import logging
from io import BytesIO
from pathlib import Path

import tqdm  # type: ignore
from minio import Minio
from nc_py_api import Nextcloud, FsNode, NextcloudException  # type: ignore

from anhaltai_commons_minio.helper_utils import normalize_minio_object_name
from anhaltai_commons_minio.io_utils import upload_object_bytes


class NextcloudMinioSub(Nextcloud):
    """
    Custom subclass of NextCloud to implement needed behavior to upload and download
    files locally and in connection with minio.
    Further documentation: https://cloud-py-api.github.io/nc_py_api/FirstSteps.html
    """

    def __init__(
        self,
        nc_auth_user,
        nc_auth_pass,
        nextcloud_url,
        **kwargs,
    ):
        super().__init__(
            nc_auth_user=nc_auth_user,
            nc_auth_pass=nc_auth_pass,
            nextcloud_url=nextcloud_url,
            **kwargs,
        )

    def file_exists(self, path: str | Path) -> bool:
        """
        Check if the file exists in the Nextcloud.
        Args:
            path (str | Path): Path to the file to check.

        Returns:
            bool: True if file exists, else False
        """
        try:
            result: FsNode = self.files.by_path(Path(path).as_posix())
            return not result.is_dir
        except NextcloudException as exception:
            if exception.status_code == 404:
                return False
        return False

    def directory_exists(self, path: str | Path) -> bool:
        """
        Check if the directory exists in the Nextcloud.
        Args:
            path (str | Path): Path to the file to check.

        Returns:
            bool: True if directory exists, else False
        """
        try:
            result: FsNode = self.files.by_path(Path(path).as_posix())
            return result.is_dir
        except NextcloudException as exception:
            if exception.status_code == 404:
                return False
        return False

    def nextcloud_directory_byte_stream_to_minio(
        self,
        minio_client: Minio,
        bucket_name: str,
        nextcloud_path: str,
        minio_path: str,
        overwrite: bool = False,
        **kwargs,
    ):
        """
        Copies a directory (and its subdirectories) from Nextcloud to minio bucket by
        using a byte stream for each file.
        Args:
            minio_client (Minio): destination Minio client
            bucket_name (str) Minio bucket name
            minio_path (str): destination file path in the Minio bucket
            nextcloud_path (str): Remote file path on Nextcloud
            overwrite (bool):  If existing files are to be overwritten
        """

        # list all files as Nodes (empty directories are ignored)
        remote_files: list[FsNode] = self.files.listdir(
            normalize_minio_object_name(nextcloud_path)
        )
        for nextcloud_file in tqdm.tqdm(remote_files):
            nextcloud_file_path = nextcloud_file.user_path

            # Construct minio file path
            relative_path: Path = Path(nextcloud_file_path).relative_to(
                Path(nextcloud_path)
            )
            target_file_path: Path = Path(minio_path) / relative_path

            # if it is a directory make recursive call
            if nextcloud_file_path.endswith("/"):
                self.nextcloud_directory_byte_stream_to_minio(
                    minio_client=minio_client,
                    bucket_name=bucket_name,
                    nextcloud_path=nextcloud_file_path,
                    minio_path=normalize_minio_object_name(target_file_path),
                    overwrite=overwrite,
                    **kwargs,
                )
            else:
                # Download the file
                self.nextcloud_file_byte_stream_to_minio(
                    minio_client=minio_client,
                    bucket_name=bucket_name,
                    nextcloud_path=nextcloud_file_path,
                    minio_path=normalize_minio_object_name(target_file_path),
                    overwrite=overwrite,
                    **kwargs,
                )

    def nextcloud_file_byte_stream_to_minio(
        self,
        minio_client: Minio,
        bucket_name: str,
        nextcloud_path: str,
        minio_path: str,
        overwrite=False,
        **kwargs,
    ) -> bool:
        """
        Copy a file from Nextcloud to minio bucket by using a byte stream.
        Args:
            minio_client (Minio): Minio client instance
            bucket_name (str): destination Minio bucket name
            nextcloud_path (str): Remote file path on Nextcloud
            minio_path (str): Target file path in minio bucket
            overwrite (bool): If existing files are to be overwritten

        Returns:
            bool: True if file was copied successfully else False
        """

        nextcloud_path = normalize_minio_object_name(nextcloud_path)
        minio_path = normalize_minio_object_name(minio_path)

        content: bytes = self.files.download(nextcloud_path)

        data_bytes = BytesIO(content)
        succeeded = upload_object_bytes(
            minio_client=minio_client,
            bucket_name=bucket_name,
            object_name=minio_path,
            data_bytes=data_bytes,
            data_length=len(content),
            overwrite=overwrite,
            **kwargs,
        )
        if succeeded:
            logging.debug("Copied: %s to %s", nextcloud_path, minio_path)
        return succeeded
