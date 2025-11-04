import click
import os
import base64
import mimetypes
from enum import Enum
from accqsure.cli import cli, pass_config


@cli.group()
@pass_config
def chart(config):
    """AccQsure chart commands."""
    pass


@chart.command()
@click.argument("document_type_id", type=click.STRING)
@pass_config
def list(config, document_type_id):
    """List charts."""
    data = [
        ["ID", "NAME", "REFERENCE_DOC", "REFERENCE_DOC_ID"],
        [
            "-" * 80,
            "-" * 80,
            "-" * 80,
            "-" * 80,
        ],
    ]
    # TODO: implement cursor function
    charts, _ = config.accqsure.run(
        config.accqsure.client.charts.list(document_type_id=document_type_id)
    )
    for chart in charts:
        data.append(
            [
                chart.id,
                chart.name,
                (
                    chart._reference_document.get("name")
                    if chart._reference_document
                    else "UNKNOWN"
                ),
                chart.reference_document_id,
            ]
        )
    for row in data:
        click.echo(
            "{: >26.24} {: >28.26} {: >28.26} {: >26.24} " "".format(*row),
            file=config.stdout,
        )
