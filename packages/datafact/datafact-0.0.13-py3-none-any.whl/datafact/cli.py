import click
from importlib.metadata import version

from datafact.subcmd.init import init_cli
from datafact.subcmd.publish import publish_cli
from datafact.subcmd.templates import templates_cli
from datafact.subcmd.experimental import experimental_cli
from datafact.subcmd.upgrade import upgrade_cli

__doc__ = f"""
    Build and publish datasets to dataset.sh
    Read more at https://doc.dataset.sh

    You are currently using dataset.sh version: {version('dataset_sh')}
"""


@click.group(help=__doc__)
def cli():
    pass


cli.add_command(init_cli, 'new')
cli.add_command(templates_cli, 'templates')
cli.add_command(publish_cli, 'publish')
cli.add_command(upgrade_cli, 'upgrade')
cli.add_command(experimental_cli, 'experimental')

if __name__ == '__main__':
    cli()
