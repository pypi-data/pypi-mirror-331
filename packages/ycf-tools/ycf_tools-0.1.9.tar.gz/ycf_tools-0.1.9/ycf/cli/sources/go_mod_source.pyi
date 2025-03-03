from ycf.cli.sources.base import BaseSource as BaseSource

class GoModSource(BaseSource):
    @property
    def include_files(self) -> set[str]: ...
