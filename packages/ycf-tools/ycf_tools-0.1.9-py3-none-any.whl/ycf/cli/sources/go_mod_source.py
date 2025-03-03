from ycf.cli.sources.base import BaseSource


class GoModSource(BaseSource):
    @property
    def include_files(self) -> set[str]:
        return super().include_files | {'go.mod', 'go.sum'}
