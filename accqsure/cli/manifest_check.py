import click
from accqsure.cli import pass_config
from accqsure.cli.manifest import manifest


@manifest.group()
@pass_config
def check(config):
    """AccQsure manifest check commands."""
    pass


@check.command()
@click.argument("manifest_id", type=click.STRING)
@pass_config
def list(config, manifest_id):
    """List manifest checks."""
    data = [
        ["ID", "SECTION", "NAME"],
        [
            "-" * 80,
            "-" * 80,
            "-" * 80,
        ],
    ]
    manifest = config.accqsure.run(config.accqsure.client.manifests.get(id=manifest_id))

    checks = config.accqsure.run(manifest.list_checks())
    for check in checks:
        data.append(
            [
                check.id,
                check.section,
                check.name,
            ]
        )
    for row in data:
        click.echo(
            "{: >26.24} {: >28.26} {: >40.38}" "".format(*row),
            file=config.stdout,
        )
