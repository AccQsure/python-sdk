import click
from accqsure.cli import cli, pass_config


@cli.group()
@pass_config
def text(config):
    """AccQsure text commands."""
    pass


@text.command()
@click.argument("prompt", type=click.STRING)
@pass_config
def generate(config, prompt):
    """
    Generate a Text Completion Response

    """

    result = config.accqsure.run(
        config.accqsure.client.text.generate([dict(role="user", content=prompt)])
    )
    click.echo(result)


@text.command()
@click.argument("text", type=click.STRING)
@pass_config
def tokenize(config, text):
    """
    Count the Tokens in a Text String

    """

    result = config.accqsure.run(config.accqsure.client.text.tokenize(text))
    click.echo(result.get("tokens"))


@text.command()
@click.argument("text", type=click.STRING)
@pass_config
def vectorize(config, text):
    """
    Convert a Text String into an Embedding Vector

    """

    result = config.accqsure.run(config.accqsure.client.text.vectorize(text))
    click.echo(result.get("vector"))
