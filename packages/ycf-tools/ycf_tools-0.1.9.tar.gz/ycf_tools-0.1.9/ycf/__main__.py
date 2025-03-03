try:
    import rich  # pyright: ignore  # noqa: F401

except ImportError:
    raise ImportError('Install ycf-tools with cli by "pip install ycf-tools[cli]"') from None


if __name__ == '__main__':
    from ycf.cli import cli

    cli()
