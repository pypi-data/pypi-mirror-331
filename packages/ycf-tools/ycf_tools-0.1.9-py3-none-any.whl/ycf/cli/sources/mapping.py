from ycf.cli import settings
from ycf.cli.sources.base import BaseSource


def get_source() -> BaseSource:
    if settings.YCFT.runtime == settings.RuntimeEnum.python312:
        if settings.YCFT.dependencies == settings.DependenciesEnum.pyproject_toml:
            from ycf.cli.sources.py_pyproject_source import PyPyprojectSource

            return PyPyprojectSource()

        if settings.YCFT.dependencies == settings.DependenciesEnum.requirements_txt:
            from ycf.cli.sources.py_requirements_source import PyRequirementsSource

            return PyRequirementsSource()

    if settings.YCFT.runtime == settings.RuntimeEnum.golang121:
        if settings.YCFT.dependencies == settings.DependenciesEnum.go_mod:
            from ycf.cli.sources.go_mod_source import GoModSource

            return GoModSource()

    raise RuntimeError(f'Incompatible settings values: {settings.YCFT.runtime=} {settings.YCFT.dependencies=}')
