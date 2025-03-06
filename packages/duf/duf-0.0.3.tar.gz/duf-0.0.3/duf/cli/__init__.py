import click

from .host import host
from .auth import auth
from .deploy import deploy


@click.group
def cli():
    pass


cli.add_command(host)
cli.add_command(auth)
cli.add_command(deploy)
