import subprocess
from pathlib import Path

import click
from fans.logger import get_logger

from .api import api


logger = get_logger(__name__)


@click.command()
def deploy():
    """Deploy current project"""
    cwd = Path().absolute()
    proj_name = cwd.name

    host = get_target_host()
    if not host:
        logger.error('failed to get target host to deploy')
        exit(1)

    execute([
        f"rsync -rav",

        f"--exclude '**/__pycache__/'",
        f"--exclude '**/node_modules/'",

        f"--include '{proj_name}/'",
        f"--include '{proj_name}/**'",

        f"--include 'frontend/'",
        f"--include 'frontend/dist/'",
        f"--include 'frontend/dist/**'",

        f"--include 'pyproject.toml'",
        f"--include 'uv.lock'",
        f"--include 'serve.sh'",

        f"--exclude '*'",

        f"./ root@{host['ip']}:/root/{proj_name}",
    ])

    execute(f"ssh root@{host['ip']} supervisorctl restart {proj_name}")


def get_target_host():
    logger.info('getting target host to deploy...')
    res = api.post('/api/host/ls')
    for host in res['hosts']:
        if host.get('name') == 'default':
            logger.info(f'got target host {host}')
            return host


def execute(cmd: str|list[str]):
    if isinstance(cmd, list):
        cmd = ' '.join(cmd)
    logger.info(f'[CMD] {cmd}')
    proc = subprocess.run(cmd, shell=True)
    if not proc.returncode == 0:
        logger.error(f'failed to execute command: {cmd}')
        exit(1)
