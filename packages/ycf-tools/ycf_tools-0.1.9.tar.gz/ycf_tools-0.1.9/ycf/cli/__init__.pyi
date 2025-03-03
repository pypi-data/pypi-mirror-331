import typer
from _typeshed import Incomplete
from ycf.cli import settings as settings
from ycf.cli.managers import DeployManager as DeployManager

cli: Incomplete
manager: Incomplete

def version_callback(value: bool) -> None: ...
def callback(ctx: typer.Context, version: bool = ..., verbose: bool = ...) -> None: ...
def deploy_command() -> None: ...
