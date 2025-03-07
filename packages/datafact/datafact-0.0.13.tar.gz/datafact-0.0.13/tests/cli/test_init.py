import os
import sys
from unittest.mock import patch, MagicMock, mock_open
import pytest
from click.testing import CliRunner
from typing_extensions import NamedTuple

from datafact.subcmd.init import init_cli, CONFIG_FILENAME


@pytest.fixture
def mock_fact_templates():
    """Fixture to mock fact_templates."""
    return [
        MagicMock(name="hello-world", create=MagicMock()),
        MagicMock(name="advanced-template", create=MagicMock()),
    ]


@pytest.fixture
def mock_is_name_legit():
    """Mock is_name_legit to always return True."""
    with patch("datafact.subcmd.init.is_name_legit", return_value=True):
        yield


@patch("datafact.subcmd.init.fact_templates")
@patch("os.makedirs")
@patch("os.path.exists", return_value=False)
@patch("datafact.subcmd.init.ProjectConfig.init_config")
def test_init_cli_success(
        mock_init_config, mock_exists, mock_makedirs, mock_fact_templates, mock_is_name_legit
):
    """Test successful initialization of a dataset project."""
    mock_create = MagicMock()

    class MockNamedTuple(NamedTuple):
        name: str = 'hello-world'
        create: MagicMock = mock_create

    mock_fact_templates.__iter__.return_value = iter([
        MockNamedTuple()
    ])

    runner = CliRunner()
    result = runner.invoke(init_cli, ["--template", "hello-world", "test_user/test_dataset"])

    # Assertions
    assert result.exit_code == 0
    assert "Project created successfully." in result.output

    # Ensure the project directory was created
    mock_makedirs.assert_called_once_with("./test_user/test_dataset", exist_ok=True)

    # Ensure the config file was initialized
    mock_init_config.assert_called_once_with("test_user/test_dataset", base_folder="./test_user/test_dataset")

    # Ensure the template's `create` method was called
    mock_create.assert_called_once_with(
        "./test_user/test_dataset",
        {
            "username": "test_user",
            "dataset_name": "test_dataset",
            "name": "test_user/test_dataset",
            "project_dir": "./test_user/test_dataset",
        },
    )


@patch("datafact.subcmd.init.fact_templates")
def test_init_cli_template_not_found(mock_fact_templates):
    """Test when the specified template is not found."""
    mock_fact_templates.__iter__.return_value = []

    runner = CliRunner()
    result = runner.invoke(init_cli, ["--template", "nonexistent-template", "test_dataset"])

    # Assertions
    assert result.exit_code == 1
    assert "Template nonexistent-template not found." in result.output


@patch("os.path.exists", return_value=True)
def test_init_cli_existing_config(mock_exists):
    """Test when the config file already exists."""
    runner = CliRunner()
    result = runner.invoke(init_cli, ["--template", "hello-world", "test_user/test_dataset"])

    # Assertions
    assert result.exit_code == 1
    assert "Config file ./test_user/test_dataset/datafact.json already exists." in result.output


@patch("os.path.basename", return_value="current_folder")
@patch("os.path.exists", return_value=False)
@patch("os.makedirs")
@patch("datafact.subcmd.init.ProjectConfig.init_config")
def test_init_cli_no_name_provided(
        mock_init_config, mock_makedirs, mock_exists, mock_basename
):
    """Test when no project name is provided."""
    runner = CliRunner()
    result = runner.invoke(init_cli, ["--template", "hello-world"])

    # Assertions
    assert result.exit_code != 0
    assert "Missing argument 'NAME'" in result.output

    # Verify that the prompt generated a name from the current folder
    # mock_makedirs.assert_called_once_with("./current_folder", exist_ok=True)
    # mock_init_config.assert_called_once_with(
    #     "local/current_folder", base_folder="./current_folder"
    # )


@patch("datafact.subcmd.init.fact_templates")
@patch("os.path.exists", return_value=False)
def test_init_cli_invalid_name(mock_exists, mock_fact_templates):
    """Test when the project name is invalid."""
    mock_create = MagicMock()

    class MockNamedTuple(NamedTuple):
        name: str = 'hello-world'
        create: MagicMock = mock_create

    mock_fact_templates.__iter__.return_value = iter([
        MockNamedTuple()
    ])

    with patch("datafact.subcmd.init.is_name_legit", return_value=False):
        runner = CliRunner()
        result = runner.invoke(init_cli, ["--template", "hello-world", "test_user/!invalid_name"])

    # Assertions
    assert result.exit_code == 1
    assert "Invalid dataset name." in result.output
