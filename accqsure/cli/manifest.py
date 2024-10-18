import click
from accqsure.cli import cli, pass_config


@cli.group()
@pass_config
def manifest(config):
    """AccQsure manifest commands."""
    pass


@manifest.command()
@click.argument("document_type_id", type=click.STRING)
@pass_config
def list(config, document_type_id):
    """List manifests."""
    data = [
        ["ID", "NAME", "REFERENCE_DOC", "REFERENCE_DOC_ID"],
        [
            "-" * 80,
            "-" * 80,
            "-" * 80,
            "-" * 80,
        ],
    ]

    manifests = config.accqsure.run(
        config.accqsure.client.manifests.list(document_type_id=document_type_id)
    )
    for manifest in manifests:
        data.append(
            [
                manifest.id,
                manifest.name,
                manifest._reference_document.get("name"),
                manifest.reference_document_id,
            ]
        )
    for row in data:
        click.echo(
            "{: >26.24} {: >28.26} {: >28.26} {: >26.24} " "".format(*row),
            file=config.stdout,
        )


from accqsure.cli.manifest_check import check
