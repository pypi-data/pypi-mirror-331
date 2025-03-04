import logging
import os

import typer

from rich.logging import RichHandler

from foreverbull_cli.bull.backtest import backtest
from foreverbull_cli.output import console


cli = typer.Typer()

cli.add_typer(backtest, name="backtest")


@cli.callback()
def setup_logging(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    very_verbose: bool = typer.Option(False, "--very-verbose", "-vv"),
    debug: bool = typer.Option(False, "-vvv"),
):
    if verbose:
        level = "WARNING"
        os.environ["LOGGING_LEVEL"] = "WARNING"
    elif very_verbose:
        level = "INFO"
        os.environ["LOGGING_LEVEL"] = "INFO"
    elif debug:
        level = "DEBUG"
        os.environ["LOGGING_LEVEL"] = "DEBUG"
    else:
        level = "ERROR"
        os.environ["LOGGING_LEVEL"] = "ERROR"
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(markup=True, console=console)],
    )
