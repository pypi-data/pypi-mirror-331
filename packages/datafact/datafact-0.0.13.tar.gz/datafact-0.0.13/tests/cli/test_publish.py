import os
import sys
from unittest.mock import patch, MagicMock
import pytest
from click.testing import CliRunner
from datafact.subcmd.publish import publish_cli, load_readme, publish_local


@pytest.fixture
def mock_load_config():
    """Mock for load_config."""
    config = MagicMock()
    config.get_target = MagicMock()
    return config


@pytest.fixture
def mock_locate_draft_file():
    """Mock for locate_draft_file."""
    return MagicMock(return_value="./dist/draft/dataset-draft.dsh")


@pytest.fixture
def mock_dataset():
    """Mock for dataset_sh.dataset."""
    dataset = MagicMock()
    dataset.import_file = MagicMock()
    dataset.set_readme = MagicMock()
    return dataset


@patch("datafact.subcmd.publish.load_config")
@patch("datafact.subcmd.publish.load_readme", return_value="Sample README content")
@patch("datafact.subcmd.publish.locate_draft_file", return_value="./dist/draft/dataset-draft.dsh")
@patch("datafact.subcmd.publish.dsh.dataset")
@patch("os.path.exists")
def test_publish_cli_success(mock_path_exists, mock_dsh_dataset, mock_locate_file, mock_load_readme, mock_load_config,
                             mock_dataset):
    """Test successful execution of publish_cli."""
    # Mock the dataset returned by dsh.dataset
    mock_path_exists.return_value = True
    mock_locate_file.return_value = "./dist/draft/dataset-draft.dsh"
    mock_load_config.return_value.get_target.return_value = {"type": "local", "name": "test_dataset"}
    mock_dsh_dataset.return_value = mock_dataset
    mock_load_readme.return_value = 'README CONTENT'

    runner = CliRunner()
    result = runner.invoke(publish_cli, ["--source", "draft", "--target", "default", "--tag", "tag1"])

    # Assertions
    assert result.exit_code == 0
    assert "done." in result.output
    mock_dataset.import_file.assert_called_once_with("./dist/draft/dataset-draft.dsh", tags=["tag1"])
    mock_dataset.set_readme.assert_called_once()


@patch("datafact.subcmd.publish.load_config")
@patch("os.path.exists")
def test_publish_cli_missing_target(mock_path_exists, mock_load_config):
    """Test publish_cli when the target is not found."""
    mock_path_exists.return_value = True
    mock_load_config.return_value.get_target.return_value = None

    runner = CliRunner()
    result = runner.invoke(publish_cli, ["--target", "unknown_target"])

    # Assertions
    assert result.exit_code == 1
    assert "Target unknown_target not found." in result.output


@patch("datafact.subcmd.publish.load_config")
@patch("datafact.subcmd.publish.locate_draft_file")
@patch("os.path.exists")
def test_publish_cli_missing_source(mock_path_exists, mock_locate_file, mock_load_config):
    """Test publish_cli when the source file is missing."""
    mock_path_exists.side_effect = lambda path: path != "./dist/draft/dataset-draft.dsh"
    mock_locate_file.return_value = "./dist/draft/dataset-draft.dsh"
    mock_load_config.return_value.get_target.return_value = {"type": "local", "name": "test_dataset"}

    runner = CliRunner()
    result = runner.invoke(publish_cli, ["--source", "draft"])

    # Assertions
    assert result.exit_code == 1
    assert "Draft dataset file ./dist/draft/dataset-draft.dsh not found." in result.output


@patch("datafact.subcmd.publish.load_readme", return_value=None)
@patch("datafact.subcmd.publish.dsh.dataset")
def test_publish_local_no_readme(mock_dataset, mock_readme):
    """Test publish_local with no README file."""
    target = {"type": "local", "name": "test_dataset"}
    source = "./dist/draft/dataset-draft.dsh"
    tags = ["tag1"]

    publish_local(source, target, tags)

    # Assertions
    mock_dataset.assert_called_once_with("test_dataset")
    mock_dataset.return_value.import_file.assert_called_once_with(source, tags=tags)
    mock_dataset.return_value.set_readme.assert_not_called()


@patch("builtins.open", new_callable=MagicMock)
def test_load_readme(mock_open):
    """Test load_readme function."""
    mock_open.return_value.__enter__.return_value.read.return_value = "README content"
    result = load_readme()
    assert result is None
    mock_open.assert_called_once_with("./README.md", "r")


@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=MagicMock)
def test_load_readme(mock_open, mock_exists):
    """Test load_readme function when the file exists."""
    # Mock file reading
    mock_open.return_value.__enter__.return_value.read.return_value = "README content"

    # Call the function
    result = load_readme()

    # Assertions
    assert result == "README content"
    mock_exists.assert_called_once_with("./README.md")  # Verify file existence was checked
    mock_open.assert_called_once_with("./README.md", "r")
