import fnmatch
import glob
import logging
import os
import zipfile
from pathlib import Path

from packaging_version_git import GitVersion

from ycf.cli import settings

logger = logging.getLogger('ycf')


class BaseSource(object):
    def __init__(self) -> None:
        pass

    @property
    def release_version(self) -> str:
        return str(GitVersion.from_commit(as_dev=True))

    @property
    def release_name(self) -> str:
        return Path.cwd().name

    @property
    def release_zip_name(self) -> str:
        return f'{settings.YCFT.s3_bucket_path}/{self.release_name}.zip'

    @property
    def release_zip_path(self) -> Path:
        return Path.cwd() / 'dist' / 'YC' / self.release_zip_name

    @property
    def include_files(self) -> set[str]:
        include_files: set[str] = set()
        exclude_files: set[str] = set()

        for files_glob in settings.YCFT.build_include:
            for file in glob.glob(files_glob, root_dir=Path.cwd(), recursive=True):
                include_files.add(file)

        for target_file in include_files:
            for files_glob in settings.YCFT.build_exclude:
                if fnmatch.fnmatch(target_file, files_glob):
                    exclude_files.add(target_file)

        include_files = include_files - exclude_files
        return {i for i in include_files if os.path.isfile(i)}

    @property
    def include_tmp_files(self) -> dict[str, str]:
        return {}

    def build(self) -> None:
        self.release_zip_path.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(self.release_zip_path, 'w') as zipf:
            for file in self.include_files:
                if not os.path.isfile(file):
                    logger.warning(f'File "{file}" not found')
                    continue

                zipf.write(file, file)

            for file_name, file_content in self.include_tmp_files.items():
                zipf.writestr(file_name, file_content)
