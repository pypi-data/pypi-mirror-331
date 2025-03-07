import os
import pytest
from unittest.mock import patch, mock_open
from datafact.proj import (
    CONFIG_FILENAME,
    ProjectConfig,
    target_to_str,
    init_project,
    locate_draft_file,
)


@pytest.fixture
def mock_config_file():
    """Fixture to mock the config file."""
    data = {
        'name': 'test_project',
        'targets': {
            'default': {
                'type': 'local',
                'name': 'test_project',
            }
        }
    }
    return data


def test_target_to_str():
    target = {'type': 'local', 'name': 'test_target'}
    label = 'test_label'
    result = target_to_str(label, target)
    assert result == "test_label: test_target"


def test_project_config_init(mock_config_file):
    config = ProjectConfig(**mock_config_file)
    assert config.name == 'test_project'
    assert 'default' in config.targets
    assert config.targets['default']['name'] == 'test_project'


@patch("builtins.open", new_callable=mock_open)
@patch("json.load")
def test_project_config_load_config(mock_json_load, mock_open_file, mock_config_file):
    mock_json_load.return_value = mock_config_file
    config = ProjectConfig.load_config()
    assert config.name == 'test_project'
    assert 'default' in config.targets
    assert config.targets['default']['name'] == 'test_project'
    mock_open_file.assert_called_once_with(CONFIG_FILENAME, 'r')


@patch("builtins.open", new_callable=mock_open)
def test_project_config_init_config(mock_open_file):
    config = ProjectConfig.init_config("new_project", "./")
    assert config.name == "new_project"
    assert "default" in config.targets
    assert config.targets["default"]["name"] == "new_project"
    mock_open_file.assert_called_once_with(os.path.join("./", CONFIG_FILENAME), "w")


def test_project_config_add_target(mock_config_file):
    config = ProjectConfig(**mock_config_file)
    config.add_target(name="new_target", label="new_label")
    assert "new_label" in config.targets
    assert config.targets["new_label"]["name"] == "new_target"


def test_project_config_remove_target(mock_config_file):
    config = ProjectConfig(**mock_config_file)
    config.add_target(name="to_be_removed", label="remove_label")
    assert "remove_label" in config.targets
    config.remove_target("remove_label")
    assert "remove_label" not in config.targets


def test_project_config_list_targets(mock_config_file):
    config = ProjectConfig(**mock_config_file)
    targets = list(config.list_targets())
    assert len(targets) == 1
    assert targets[0][0] == "default"
    assert targets[0][1]["name"] == "test_project"


@patch("builtins.open", new_callable=mock_open)
def test_project_config_save(mock_open_file, mock_config_file):
    config = ProjectConfig(**mock_config_file)
    config.save()
    mock_open_file.assert_called_once_with(CONFIG_FILENAME, "w")


@patch("os.path.join", return_value="/dist/test_project/dataset-draft.dsh")
def test_locate_draft_file(mock_path_join):
    file_path = locate_draft_file("test_project")
    assert file_path == "/dist/test_project/dataset-draft.dsh"
    mock_path_join.assert_called_once_with("./dist", "test_project", "dataset-draft.dsh")


@patch("builtins.open", new_callable=mock_open)
def test_init_project(mock_open_file):
    init_project("test_project")
    mock_open_file.assert_called_once()
