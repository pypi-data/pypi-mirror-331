from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
from ycf.cli import settings as settings
from ycf.cli.yc.dto import YandexCloudFunctionRelease as YandexCloudFunctionRelease

class StaticKeyAccessResponse(BaseModel):
    id: str
    serviceAccountId: str
    createdAt: str
    description: str
    keyId: str
    lastUsedAt: datetime | None

class StaticKeyResponse(BaseModel):
    accessKey: StaticKeyAccessResponse
    secret: str

class IamTokenResponse(BaseModel):
    iamToken: str
    expiresAt: datetime

class YandexCloudClient:
    iam_token: IamTokenResponse | None
    static_key: StaticKeyResponse | None
    def __init__(self) -> None: ...
    def auth_iam_token(self) -> None: ...
    def auth_static_key(self) -> None: ...
    def yandex_cloud_function_release(self, ycf_release: YandexCloudFunctionRelease) -> YandexCloudFunctionRelease: ...
    def delete_access_key(self) -> None: ...
    def s3_updated_file(self, bucket_name: str, file_path: Path, file_name: str) -> None: ...
