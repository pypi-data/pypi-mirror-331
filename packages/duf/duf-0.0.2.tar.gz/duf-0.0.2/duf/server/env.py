from fans.path import Path, make_paths


class Env:

    def __init__(self):
        self.reset()

    def reset(self, root = ''):
        self.paths = make_paths(Path(root), [
            'data', [
                'hosts.json', {'hosts'},
            ],
        ])


env = Env()
