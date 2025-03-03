import typer

import ycf
from ycf.cli import settings
from ycf.cli.managers import DeployManager

cli = typer.Typer(help='ycf CLI')

manager = DeployManager()


def version_callback(value: bool) -> None:
    if value:
        print(f'Version of ycf is {ycf.__version__}')
        raise typer.Exit(0)


@cli.callback(invoke_without_command=True)
def callback(  # noqa: C901
    ctx: typer.Context,
    #
    version: bool = typer.Option(
        False,
        '--version',
        callback=version_callback,
        help='Print version of ycf.',
        is_eager=True,
    ),
    #
    verbose: bool = typer.Option(
        False,
        '--verbose',
        '-v',
        help='Run with verbose',
    ),
) -> None:
    settings.YCFT.set_settings(
        verbose=verbose,
    )


@cli.command('deploy', hidden=True)
def deploy_command() -> None:
    print('Authenticating...')
    manager.auth()

    print('Building...')
    manager.build()

    print('Uploading...')
    manager.upload()

    print('Releasing...')
    manager.release()

    print('Cleaning...')
    manager.clean()
