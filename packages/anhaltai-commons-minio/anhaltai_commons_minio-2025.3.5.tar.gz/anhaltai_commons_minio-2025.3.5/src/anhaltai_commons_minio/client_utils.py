"""
Contains functions for operations with Minio clients such as customized getter for
Minio clients
"""

import logging
import os

from dotenv import load_dotenv
from minio import Minio


def get_client(
    access_key_env_name: str = "MINIO_ACCESS_KEY",
    secret_key_env_name: str = "MINIO_SECRET_KEY",
    endpoint: str = "localhost:9000",
    secure: bool = True,
    cert_check: bool = False,
    session_token=None,
    region=None,
    http_client=None,
    credentials=None,
) -> Minio:
    """
    Get Simple Storage Service (aka S3) client for Minio to perform bucket and object
    operations. The function is a shortcut for the Minio constructor by loading the
    access and secret key from the addressed env variables.

    Read about the usage of the Minio constructor here:
    https://min.io/docs/minio/linux/developers/python/API.html.

    :param endpoint: Hostname of an S3 service ip:port.
    :param access_key_env_name: Name of the env variable that provides the access key
    (aka user ID) of your account in S3 service.
    :param secret_key_env_name: Name of the env variable that provides the secret Key
    (aka password) of your account in S3 service.
    :param session_token: Session token of your account in S3 service.
    :param secure: Flag to indicate to use secure (TLS) connection to S3
        service or not.
    :param region: Region name of buckets in S3 service.
    :param http_client: Customized HTTP client.
    :param credentials: Credentials provider of your account in S3 service.
    :param cert_check: Flag to indicate to verify SSL certificate or not.
    :return: :class:`Minio <Minio>` object
    """

    load_dotenv()
    minio_access_key = os.getenv(access_key_env_name)
    minio_secret_key = os.getenv(secret_key_env_name)

    logging.info("Initialize Minio client on endpoint %s", endpoint)
    minio_client: Minio = Minio(
        endpoint=endpoint,
        session_token=session_token,
        access_key=minio_access_key,
        secret_key=minio_secret_key,
        secure=secure,
        region=region,
        http_client=http_client,
        credentials=credentials,
        cert_check=cert_check,
    )
    return minio_client
