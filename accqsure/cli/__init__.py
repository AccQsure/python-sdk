import asyncio
import click
import logging
from os import devnull
from sys import stderr, stdout


from accqsure.accqsure import AccQsure


class AccQsureRunner(object):
    def __init__(self):
        self._accqsure_client = None

    @property
    def client(self) -> AccQsure:
        if self._accqsure_client is None:
            try:
                self._accqsure_client = AccQsure()
            except Exception as err:
                raise click.UsageError(err)
        return self._accqsure_client

    async def _run(self, *tasks):
        return await asyncio.gather(*tasks)

    def run(self, *tasks):
        try:
            if len(tasks) == 1:
                return_value = asyncio.run(*tasks)
            else:
                return_value = asyncio.run(self._run(*tasks))
        except Exception as err:
            raise click.UsageError(err)
        return return_value


class Config(object):
    def __init__(self):
        self.stderr = stderr
        self.stdout = stdout
        self.accqsure = AccQsureRunner()


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.version_option(package_name="accqsure", prog_name="AccQsure CLI and SDK")
@click.option(
    "--debug",
    "-d",
    is_flag=True,
    type=click.BOOL,
    default=False,
    help="Show debug output.",
)
@click.option(
    "--output-file",
    "-o",
    type=click.File("w"),
    default="-",
    help="Send output to file.",
)
@click.option(
    "--silent",
    "-s",
    is_flag=True,
    type=click.BOOL,
    default=False,
    help="Silence all output.",
)
@click.option(
    "--verbose",
    "-v",
    "verbosity",
    count=True,
    type=click.INT,
    default=0,
    help="Specify verbosity (repeat to increase).",
)
@pass_config
def cli(config, debug, output_file, silent, verbosity):
    """AccQsure command-line interface."""
    config.stdout = output_file

    if debug or verbosity > 0:
        if silent:
            click.echo(
                "Ignoring silent flag when debug or verbosity is set.",
                file=config.stderr,
            )
        if verbosity == 1:
            verbosity = logging.INFO
        else:
            verbosity = logging.DEBUG
    elif silent:
        config.stderr = config.stdout = open(devnull, "w")
    else:
        verbosity = logging.WARNING

    if verbosity != logging.WARNING:  # default
        click.echo(
            f"Verbosity set to {logging.getLevelName(verbosity)}",
            file=config.stderr,
        )

    logging.basicConfig(
        format="%(asctime)s.%(msecs)03dZ  %(levelname)s  %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        level=verbosity,
        stream=config.stderr,
        force=True,
    )


from accqsure.cli.text import text
from accqsure.cli.document import document
from accqsure.cli.document_type import document_type
from accqsure.cli.manifest import manifest
