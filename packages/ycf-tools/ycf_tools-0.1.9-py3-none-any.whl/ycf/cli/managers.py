from ycf.cli import settings
from ycf.cli.sources.mapping import get_source
from ycf.cli.yc.client import YandexCloudClient
from ycf.cli.yc.dto import YandexCloudFunctionRelease


class DeployManager(object):
    def __init__(self) -> None:
        self.yc_client = YandexCloudClient()
        self.source = get_source()

    def auth(self) -> None:
        self.yc_client.auth_iam_token()
        self.yc_client.auth_static_key()

    def build(self) -> None:
        self.source.build()

    def upload(self) -> None:
        self.yc_client.s3_updated_file(
            settings.YCFT.s3_bucket_name,
            self.source.release_zip_path,
            self.source.release_zip_name,
        )

    def release(self) -> None:
        self.yc_client.yandex_cloud_function_release(
            YandexCloudFunctionRelease(
                id=settings.YCFT.id,
                runtime=str(settings.YCFT.runtime),
                entrypoint=settings.YCFT.entrypoint,
                memory=settings.YCFT.memory,
                environment=settings.YCFT.environment,
                service_account_id=settings.YCFT.service_account_id,
                s3_bucket_name=settings.YCFT.s3_bucket_name,
                object_name=self.source.release_zip_name,
                release_name=self.source.release_name,
                release_version=self.source.release_version,
            )
        )

    def clean(self) -> None:
        self.yc_client.delete_access_key()
