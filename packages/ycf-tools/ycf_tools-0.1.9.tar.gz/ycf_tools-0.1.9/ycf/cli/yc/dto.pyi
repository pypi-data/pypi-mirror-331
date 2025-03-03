from dataclasses import dataclass
from typing import Any

@dataclass
class YandexCloudFunctionRelease:
    id: str
    runtime: str
    entrypoint: str
    memory: int
    environment: dict[str, Any]
    service_account_id: str
    s3_bucket_name: str
    object_name: str
    release_name: str
    release_version: str
    @property
    def release_version_pretty(self) -> str: ...
