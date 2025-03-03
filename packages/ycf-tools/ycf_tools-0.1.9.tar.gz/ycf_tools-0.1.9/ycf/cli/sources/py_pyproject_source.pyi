from ycf.cli.sources.base import BaseSource as BaseSource
from ycf.cli.utils.requirements_converter import RequirementsConverter as RequirementsConverter

class PyPyprojectSource(BaseSource):
    @property
    def include_tmp_files(self) -> dict[str, str]: ...
