import getpass
import subprocess
from pathlib import Path

import click
from fans.logger import get_logger

from .api import api


logger = get_logger(__name__)


@click.group()
def auth():
    """Authorization"""
    pass


@auth.command()
def login():
    username = input('Username: ')
    password = getpass.getpass()
    res = api.post('https://auth.fans656.me/api/login', {
        'username': username,
        'password': password,
    })
    print(res.json())
