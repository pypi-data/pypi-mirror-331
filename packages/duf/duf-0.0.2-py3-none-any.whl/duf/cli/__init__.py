import click

from .host import host
from .deploy import deploy


@click.group
def cli():
    pass


cli.add_command(host)
cli.add_command(deploy)
