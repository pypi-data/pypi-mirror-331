import uuid
from typing import Optional

from fastapi import FastAPI, Body, HTTPException
from fansauth import auth

from .env import env


app = auth(FastAPI(), login='api')


@app.post('/api/host/ls')
def host_ls():
    return {'hosts': list(Hosts())}


@app.post('/api/host/info')
def host_info(req: dict):
    host = Hosts().find(req['target'])
    if host:
        return host
    else:
        raise HTTPException(404)


@app.post('/api/host/add')
def host_add(host: dict):
    host_id = Hosts().add(host)
    return {'id': host_id}


@app.post('/api/host/edit')
def host_edit(update: dict):
    host = Hosts().update(update)
    if host:
        return host
    else:
        raise HTTPException(404)


@app.post('/api/host/remove')
def host_remove(req: dict):
    host = Hosts().remove(req['target'])
    if host:
        return host
    else:
        raise HTTPException(404)


class Hosts:

    def __init__(self):
        self.meta = env.paths.hosts.as_meta(default={
            'hosts': [],
        })

    def add(self, host: dict) -> Optional[str]:
        host.setdefault('id', uuid.uuid4().hex)
        self.meta['hosts'].append(host)
        self.meta.save()
        return host['id']

    def update(self, update: dict):
        host = self.get(update['id'])
        if host:
            host.update(update)
            self.meta.save()
            return host
        else:
            return None

    def find(self, target: str):
        for host in self:
            if is_target(host, target):
                return host

    def get(self, host_id: str):
        return next((d for d in self if d['id'] == host_id), None)

    def remove(self, target: str):
        host = self.find(target)
        if host:
            self.meta['hosts'] = [d for d in self if not is_target(d, target)]
            self.meta.save()
            return host

    def __iter__(self):
        for host in self.meta['hosts']:
            yield host

    def __contains__(self, host_id: str):
        return any(host_id == host['id'] for host in self)


def is_target(host: dict, target: str):
    if host['id'] == target:
        return True
    if host['name'] == target:
        return True
    return False
