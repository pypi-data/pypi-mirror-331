import os
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from datafact.subcmd.build import get_build_command


@pytest.fixture
def mock_create_data_dict():
    """Mock for the create_data_dict function."""
    return MagicMock(return_value={"key": "value"})


@pytest.fixture
def mock_data_types():
    """Mock for the data_types dictionary."""
    return {"key": "type"}


@patch("datafact.subcmd.build.version", return_value="1.0.0")
@patch("datafact.subcmd.build.locate_draft_file", return_value="./dist/dataset-draft.dsh")
@patch("datafact.subcmd.build.dump_collections")
@patch("os.path.exists", return_value=False)
def test_build_cli_success(mock_path_exists, mock_dump_collections, mock_locate_file, mock_version,
                           mock_create_data_dict, mock_data_types):
    """Test successful execution of build_cli."""
    build_cli = get_build_command(mock_create_data_dict, mock_data_types)

    runner = CliRunner()
    result = runner.invoke(build_cli, ["--name", "draft", "--message", "Initial draft"])

    # Assertions
    assert result.exit_code == 0
    assert "You are building with dataset.sh version: 1.0.0" in result.output
    assert "creating dataset.sh file at ./dist/dataset-draft.dsh" in result.output
    assert "done." in result.output

    # Verify locate_draft_file was called
    mock_locate_file.assert_called_once_with("draft")

    # Verify dump_collections was called
    mock_dump_collections.assert_called_once_with(
        "./dist/dataset-draft.dsh",
        mock_create_data_dict.return_value,
        type_dict=mock_data_types,
        description="Initial draft",
    )


@patch("datafact.subcmd.build.version", return_value="1.0.0")
@patch("datafact.subcmd.build.locate_draft_file", return_value="./dist/dataset-draft.dsh")
@patch("datafact.subcmd.build.dump_collections")
@patch("os.path.exists", return_value=True)
def test_build_cli_overwrite(mock_path_exists, mock_dump_collections, mock_locate_file, mock_version,
                             mock_create_data_dict, mock_data_types):
    """Test build_cli with overwrite option."""
    build_cli = get_build_command(mock_create_data_dict, mock_data_types)

    runner = CliRunner()
    result = runner.invoke(build_cli, ["--name", "draft", "--message", "Updated draft", "--overwrite"])

    # Assertions
    assert result.exit_code == 0
    assert "removing existing file at ./dist/dataset-draft.dsh" in result.output
    assert "creating dataset.sh file at ./dist/dataset-draft.dsh" in result.output
    assert "done." in result.output

    # Verify locate_draft_file was called
    mock_locate_file.assert_called_once_with("draft")

    # Verify dump_collections was called
    mock_dump_collections.assert_called_once_with(
        "./dist/dataset-draft.dsh",
        mock_create_data_dict.return_value,
        type_dict=mock_data_types,
        description="Updated draft",
    )


@patch("datafact.subcmd.build.version", return_value="1.0.0")
@patch("datafact.subcmd.build.locate_draft_file", return_value="./dist/dataset-draft.dsh")
@patch("os.path.exists", return_value=True)
def test_build_cli_existing_file_no_overwrite(mock_path_exists, mock_locate_file, mock_version):
    """Test build_cli when file exists and overwrite is not specified."""
    build_cli = get_build_command(lambda: {}, {})

    runner = CliRunner()
    result = runner.invoke(build_cli, ["--name", "draft"])

    # Assertions
    assert result.exit_code == 1
    assert "dataset.sh file already exists at ./dist/dataset-draft.dsh" in result.output


@patch("datafact.subcmd.build.version", return_value="1.0.0")
@patch("datafact.subcmd.build.dump_collections")
@patch("datafact.subcmd.build.locate_draft_file", return_value="./dist/dataset-draft.dsh")
@patch("os.path.exists", return_value=True)
def test_build_cli_missing_name(mock_path_exists, mock_locate_file, mock_dump_collections, mock_version):
    """Test build_cli with default name when --name is not provided."""
    build_cli = get_build_command(lambda: {}, {})

    runner = CliRunner()
    result = runner.invoke(build_cli, ['-o'])

    # Assertions
    assert result.exit_code == 0
    assert "creating dataset.sh file at ./dist/dataset-draft.dsh" in result.output
    mock_dump_collections.assert_called_once_with(
        "./dist/dataset-draft.dsh",
        {},
        type_dict={},
        description="",
    )
