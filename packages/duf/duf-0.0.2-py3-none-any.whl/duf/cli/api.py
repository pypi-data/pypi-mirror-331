import os
import json

import click
import requests


class API:

    def __init__(self):
        self.origin = 'https://duf.fans656.me'

    def post(self, path, req: dict = {}):
        res = requests.post(
            f'{self.origin}{path}',
            json=req,
            cookies={'token': os.environ.get('TOKEN')},
        )
        if res.status_code == 200:
            return res.json()
        else:
            try:
                click.echo(json.dumps(res.json(), indent=2))
            except:
                click.echo(res.text)
            click.echo(click.style(f'ERROR: {res.status_code}', fg='red'))


api = API()
