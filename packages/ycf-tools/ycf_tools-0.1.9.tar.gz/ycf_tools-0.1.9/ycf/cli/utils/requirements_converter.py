import tomllib
from pathlib import Path


class RequirementsConverter:
    def __init__(self, project_dir: str | Path, with_version: bool = True) -> None:
        self.__project_dir = Path(project_dir).resolve(strict=True)
        self.__source = self.__project_dir / 'pyproject.toml'
        self.__target = self.__project_dir / 'requirements.txt'

        self.__with_version = with_version

    @property
    def dependencies(self) -> list[str]:
        content: dict[str, dict[str, list[str]]] = {}

        with self.__source.open('rb') as f:
            content = tomllib.load(f)

        return content.get('project', {}).get('dependencies', [])

    @property
    def requirements_txt_str(self) -> str:
        return '\n'.join(self.dependencies)

    def save_as_requirements_txt(self) -> None:
        self.__target.write_text(self.requirements_txt_str)
