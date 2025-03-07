import json
import os
from typing import TypedDict, Literal, Union

CONFIG_FILENAME = 'datafact.json'
DEFAULT_TARGET = 'default'


class DatasetLocalTarget(TypedDict):
    type: Literal['local']
    name: str


def target_to_str(label: str, target: DatasetLocalTarget):
    return f"{label}: {target['name']}"


class ProjectConfig:
    name: str
    targets: dict[str, DatasetLocalTarget]

    def __init__(self, name, targets):
        self.name = name
        self.targets = targets

    @staticmethod
    def load_config():
        with open(CONFIG_FILENAME, 'r') as f:
            data = json.load(f)
            return ProjectConfig(**data)

    @staticmethod
    def init_config(name: str, base_folder='./'):
        init_config = {
            'name': name,
            'targets': {
                'default': {
                    'type': 'local',
                    'name': name,
                }
            }
        }

        fp = os.path.join(base_folder, CONFIG_FILENAME)

        with open(fp, 'w') as f:
            json.dump(init_config, f, indent=4, sort_keys=True)
            return ProjectConfig(**init_config)

    def get_target(self, label='default'):
        target = self.targets.get(label)
        return target

    def add_target(self, name, label='default'):
        self.targets[label] = dict(
            type='local',
            name=name,
        )

    def remove_target(self, label):
        del self.targets[label]

    def list_targets(self):
        for label, target in self.targets.items():
            yield label, target

    def publish(self, source_file, target_def):
        pass

    def save(self):
        with open(CONFIG_FILENAME, 'w') as f:
            json.dump({
                'name': self.name,
                'targets': self.targets,
            }, f)

    def get_render_context(self, project_dir='./'):
        username, dataset_name = self.name.split('/')
        return {
            'username': username,
            'dataset_name': dataset_name,
            'name': self.name,
            'project_dir': project_dir
        }


load_config = ProjectConfig.load_config


def init_project(name: str):
    """
    createCONFIG_FILENAME file
    create type.py
    create
    :return:
    """
    if '/' not in name:
        name = 'local/' + name

    ProjectConfig.init_config(name)


def locate_draft_file(file_name):
    return os.path.join('./dist', file_name, 'dataset-draft.dsh')
