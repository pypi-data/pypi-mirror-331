import time
from datetime import datetime
from pathlib import Path
from typing import Any

import boto3
import httpx
import jwt
from pydantic import BaseModel

from ycf.cli import settings
from ycf.cli.yc.dto import YandexCloudFunctionRelease


class StaticKeyAccessResponse(BaseModel):
    id: str
    serviceAccountId: str
    createdAt: str
    description: str
    keyId: str
    lastUsedAt: datetime | None = None


class StaticKeyResponse(BaseModel):
    accessKey: StaticKeyAccessResponse
    secret: str


class IamTokenResponse(BaseModel):
    iamToken: str
    expiresAt: datetime


class YandexCloudClient(object):
    iam_token: IamTokenResponse | None
    static_key: StaticKeyResponse | None

    def __init__(self) -> None:
        self.iam_token = None
        self.static_key = None

    def auth_iam_token(self) -> None:
        auth_url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'

        now = int(time.time())
        payload: dict[str, Any] = {
            'aud': auth_url,
            'iss': settings.YCFT.service_account_id,
            'iat': now,
            'exp': now + 3600,
        }

        encoded_token = jwt.encode(
            payload,
            settings.YCFT.authorized_key_data.private_key,
            algorithm='PS256',
            headers={
                'kid': settings.YCFT.authorized_key_data.id,
            },
        )

        response = httpx.post(
            auth_url,
            headers={
                'Content-Type': 'application/json',
            },
            json={
                'jwt': encoded_token,
            },
        )

        response.raise_for_status()
        self.iam_token = IamTokenResponse.model_validate(response.json())

    def auth_static_key(self) -> None:
        assert self.iam_token is not None

        response = httpx.post(
            'https://iam.api.cloud.yandex.net/iam/aws-compatibility/v1/accessKeys',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.iam_token.iamToken}',
            },
            json={
                'serviceAccountId': settings.YCFT.service_account_id,
                'description': 'Temporary AwsAccessKey by ycf.cli',
            },
        )

        if response.status_code == 403:
            raise RuntimeError(
                'Service account must have those permissions:',
                'iam.serviceAccounts.accessKeyAdmin, iam.serviceAccounts.user',
            )

        response.raise_for_status()
        self.static_key = StaticKeyResponse.model_validate(response.json())

    def yandex_cloud_function_release(self, ycf_release: YandexCloudFunctionRelease) -> YandexCloudFunctionRelease:
        assert self.iam_token is not None
        assert self.static_key is not None

        data: dict[str, Any] = {
            'functionId': ycf_release.id,
            'runtime': ycf_release.runtime,
            'entrypoint': ycf_release.entrypoint,
            'resources': {
                'memory': str(ycf_release.memory),
            },
            'executionTimeout': '5s',
            'serviceAccountId': ycf_release.service_account_id,
            'package': {
                'bucketName': ycf_release.s3_bucket_name,
                'objectName': ycf_release.object_name,
            },
            'environment': ycf_release.environment,
            'description': f'Deployed {ycf_release.runtime}:',
            'tag': ['ycf', ycf_release.release_name, ycf_release.release_version_pretty],
        }

        response = httpx.post(
            'https://serverless-functions.api.cloud.yandex.net/functions/v1/versions',
            headers={
                'Authorization': f'Bearer {self.iam_token.iamToken}',
            },
            json=data,
        )

        try:
            response.raise_for_status()

        except BaseException as ex:
            raise RuntimeError(response.json()) from ex

        return ycf_release

    def delete_access_key(self) -> None:
        assert self.iam_token is not None
        assert self.static_key is not None

        response = httpx.delete(
            f'https://iam.api.cloud.yandex.net/iam/aws-compatibility/v1/accessKeys/{self.static_key.accessKey.id}',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.iam_token.iamToken}',
            },
        )
        response.raise_for_status()

    def s3_updated_file(self, bucket_name: str, file_path: Path, file_name: str) -> None:
        assert self.iam_token is not None
        assert self.static_key is not None

        s3 = boto3.client(  # pyright: ignore
            service_name='s3',
            endpoint_url=settings.YCFT.s3_endpoint_url,
            region_name=settings.YCFT.s3_region_name,
            aws_access_key_id=self.static_key.accessKey.keyId,
            aws_secret_access_key=self.static_key.secret,
        )
        s3.upload_file(  # pyright: ignore
            file_path,
            bucket_name,
            file_name,
        )
