from pathlib import Path
import json


def save_bunch(bunch, path):
    with open(path, 'w') as fp:
        json.dump(bunch, fp)


def load_bunch(self, path):
    with open(path) as fp:
        bunch = json.load(fp)
    return bunch


def mkdir(root_dir):
    '''依据给定名称创建目录'''
    path = Path(root_dir)
    if not path.exists():
        path.mkdir()
