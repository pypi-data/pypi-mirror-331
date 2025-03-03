from pathlib import Path

from ycf.cli.sources.base import BaseSource
from ycf.cli.utils.requirements_converter import RequirementsConverter


class PyPyprojectSource(BaseSource):
    @property
    def include_tmp_files(self) -> dict[str, str]:
        files: dict[str, str] = {}

        convector = RequirementsConverter(Path.cwd(), with_version=False)
        files['requirements.txt'] = convector.requirements_txt_str

        return files
