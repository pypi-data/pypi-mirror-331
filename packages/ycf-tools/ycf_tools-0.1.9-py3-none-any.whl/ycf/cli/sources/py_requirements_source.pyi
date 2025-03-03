from ycf.cli.sources.base import BaseSource as BaseSource

class PyRequirementsSource(BaseSource):
    @property
    def include_files(self) -> set[str]: ...
