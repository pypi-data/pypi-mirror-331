import logging
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Self

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

logger = logging.getLogger('ycf')


class RuntimeEnum(StrEnum):
    python312 = 'python312'
    golang121 = 'golang121'


class DependenciesEnum(StrEnum):
    pyproject_toml = 'pyproject.toml'
    requirements_txt = 'requirements.txt'
    go_mod = 'go.mod'


RUNTIME_DEPENDENCIES_MACH = {
    RuntimeEnum.python312: {DependenciesEnum.pyproject_toml, DependenciesEnum.requirements_txt},
    RuntimeEnum.golang121: {
        DependenciesEnum.go_mod,
    },
}


class AuthorizedKey(BaseModel):
    id: str
    service_account_id: str
    created_at: datetime
    key_algorithm: str
    public_key: str
    private_key: str


class YcftSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path.cwd() / '.env',
        toml_file=Path.cwd() / 'ycf.toml',
        pyproject_toml_table_header=('tool', 'ycf'),
        env_prefix='YCF_',
        extra='ignore',
        case_sensitive=False,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            PyprojectTomlConfigSettingsSource(
                settings_cls,
                toml_file=Path.cwd() / 'pyproject.toml',
            ),
            TomlConfigSettingsSource(
                settings_cls,
                toml_file=Path.cwd() / 'ycf.toml',
            ),
            dotenv_settings,
            env_settings,
        )

    runtime: RuntimeEnum = RuntimeEnum.python312
    dependencies: DependenciesEnum | None = None

    authorized_key: str = 'authorized_key.json'
    service_account_id: str

    build_dependencies_groups: list[str] = []
    build_include: list[str] = [
        '*.py',
        '**/*.py',
        '*.go',
        '**/*.go',
        'assess/*',
        'requirements.txt',
        'go.mod',
        'go.sum',
    ]
    build_exclude: list[str] = ['**/__pycache__/**', 'tests/*', 'dist/*', 'build/*', 'venv/*', 'node_modules/*']

    s3_bucket_name: str
    s3_bucket_path: str = 'functions'

    id: str
    entrypoint: str = 'main.handler'
    memory: int = 134217728
    environment: dict[str, Any] = Field(default_factory=dict)

    s3_endpoint_url: str = 'https://storage.yandexcloud.net'
    s3_region_name: str = 'ru-central1'

    verbose: bool = False

    @model_validator(mode='after')
    def validate_dependencies(self) -> Self:
        # pp(self.dict())
        # exit(0)
        if self.runtime == RuntimeEnum.python312 and self.dependencies is None:
            self.dependencies = DependenciesEnum.pyproject_toml

        if self.runtime == 'golang121' and self.dependencies is None:
            self.dependencies = DependenciesEnum.go_mod

        if self.dependencies not in RUNTIME_DEPENDENCIES_MACH[self.runtime]:
            raise RuntimeError(f'Incompatible settings values: {self.runtime=} {self.dependencies=}')

        return self

    @property
    def authorized_key_data(self) -> AuthorizedKey:
        file = Path(self.authorized_key)
        return AuthorizedKey.model_validate_json(file.read_text())

    def set_settings(self, verbose: bool) -> None:
        self.verbose = verbose


YCFT = YcftSettings()  # type: ignore
