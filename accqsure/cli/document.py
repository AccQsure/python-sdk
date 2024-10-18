import click
from accqsure.cli import cli, pass_config


@cli.group()
@pass_config
def document(config):
    """AccQsure document commands."""
    pass


@document.command()
@click.argument("document_type_id", type=click.STRING)
@pass_config
def list(config, document_type_id):
    """List documents."""
    data = [
        ["ID", "NAME", "DOC_ID"],
        [
            "-" * 80,
            "-" * 80,
            "-" * 80,
        ],
    ]

    documents = config.accqsure.run(
        config.accqsure.client.documents.list(document_type_id=document_type_id)
    )
    for doc in documents:
        data.append(
            [
                doc.id,
                doc.name,
                doc.doc_id,
            ]
        )
    for row in data:
        click.echo(
            "{: >26.24} {: >40.38} {: >14.12} " "".format(*row),
            file=config.stdout,
        )
