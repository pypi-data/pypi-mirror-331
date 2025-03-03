from _typeshed import Incomplete
from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource as PydanticBaseSettingsSource
from typing import Any, Self

logger: Incomplete

class RuntimeEnum(StrEnum):
    python312 = 'python312'
    golang121 = 'golang121'

class DependenciesEnum(StrEnum):
    pyproject_toml = 'pyproject.toml'
    requirements_txt = 'requirements.txt'
    go_mod = 'go.mod'

RUNTIME_DEPENDENCIES_MACH: Incomplete

class AuthorizedKey(BaseModel):
    id: str
    service_account_id: str
    created_at: datetime
    key_algorithm: str
    public_key: str
    private_key: str

class YcftSettings(BaseSettings):
    model_config: Incomplete
    @classmethod
    def settings_customise_sources(cls, settings_cls: type[BaseSettings], init_settings: PydanticBaseSettingsSource, env_settings: PydanticBaseSettingsSource, dotenv_settings: PydanticBaseSettingsSource, file_secret_settings: PydanticBaseSettingsSource) -> tuple[PydanticBaseSettingsSource, ...]: ...
    runtime: RuntimeEnum
    dependencies: DependenciesEnum | None
    authorized_key: str
    service_account_id: str
    build_dependencies_groups: list[str]
    build_include: list[str]
    build_exclude: list[str]
    s3_bucket_name: str
    s3_bucket_path: str
    id: str
    entrypoint: str
    memory: int
    environment: dict[str, Any]
    s3_endpoint_url: str
    s3_region_name: str
    verbose: bool
    def validate_dependencies(self) -> Self: ...
    @property
    def authorized_key_data(self) -> AuthorizedKey: ...
    def set_settings(self, verbose: bool) -> None: ...

YCFT: Incomplete
