import click
from accqsure.cli import cli, pass_config


@cli.group()
@pass_config
def document_type(config):
    """AccQsure document_type commands."""
    pass


@document_type.command()
@pass_config
def list(config):
    """List document types."""
    data = [
        ["ID", "NAME", "CODE"],
        [
            "-" * 80,
            "-" * 80,
            "-" * 80,
        ],
    ]

    documents = config.accqsure.run(config.accqsure.client.document_types.list())
    for doc in documents:
        data.append(
            [
                doc.id,
                doc.name,
                doc.code,
            ]
        )
    for row in data:
        click.echo(
            "{: >26.24} {: >40.38} {: >14.12} " "".format(*row),
            file=config.stdout,
        )
