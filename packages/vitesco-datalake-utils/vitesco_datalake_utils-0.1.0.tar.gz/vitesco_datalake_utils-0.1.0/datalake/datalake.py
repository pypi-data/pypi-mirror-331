import os

import boto3
import requests
from aws_lambda_powertools import Logger
from mypy_boto3_s3.client import S3Client

logger = Logger()


DATALAKE_REQUEST_TIMEOUT_S = int(os.getenv("DATALAKE_REQUEST_TIMEOUT_S", "2"))
logger.debug(
    "set timeout for datalake api requests",
    extra={"timeout": DATALAKE_REQUEST_TIMEOUT_S},
)


def get_credentials(token: str) -> dict:
    datalake_api_url = os.environ["DATALAKE_API_URL"]

    response = requests.get(
        f"{datalake_api_url}/s3/credentials",
        headers={
            "Authorization": token,
        },
        timeout=DATALAKE_REQUEST_TIMEOUT_S,
    )
    _verify_datalake_api_response(response)
    return response.json()


def get_s3_boto_client(token: str) -> S3Client:
    creds = get_credentials(token)
    logger.info("creating new s3 client...")
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
    )
    return s3_client


def get_datasets(token: str) -> dict:
    datalake_api_url = os.environ["DATALAKE_API_URL"]
    response = requests.get(
        f"{datalake_api_url}/s3",
        headers={
            "Authorization": token,
        },
        timeout=DATALAKE_REQUEST_TIMEOUT_S,
    )
    _verify_datalake_api_response(response)

    logger.debug(
        "Datalake API response",
        status_code=response.status_code,
        content=response.content,
    )

    return response.json()


def _verify_datalake_api_response(response: requests.Response) -> None:
    if response.status_code != 200:
        logger.error(
            "Datalake API request failed",
            status_code=response.status_code,
            content=response.content,
        )
        raise Exception("Datalake API error")
