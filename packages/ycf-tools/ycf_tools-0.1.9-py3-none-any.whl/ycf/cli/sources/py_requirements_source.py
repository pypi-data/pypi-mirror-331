from ycf.cli.sources.base import BaseSource


class PyRequirementsSource(BaseSource):
    @property
    def include_files(self) -> set[str]:
        return super().include_files | {'requirements.txt'}
