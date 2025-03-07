import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from datafact.subcmd.preview import preview_cli


@pytest.fixture
def mock_locate_draft_file():
    """Mock for locate_draft_file."""
    return "./dist/dataset-draft.dsh"


@pytest.fixture
def mock_open_dataset_file():
    """Mock for dataset_sh.open_dataset_file."""
    mock_file = MagicMock()
    mock_file.collection = MagicMock(return_value=[{"id": 1, "name": "item1"}, {"id": 2, "name": "item2"}])
    mock_file.collections = MagicMock(return_value=["collection1", "collection2"])
    return mock_file


@patch("datafact.subcmd.preview.locate_draft_file", return_value="./dist/dataset-draft.dsh")
@patch("os.path.exists", return_value=True)
@patch("datafact.subcmd.preview.dataset_sh.open_dataset_file")
def test_preview_collection_success(mock_open, mock_exists, mock_locate):
    """Test preview_collection command with a valid dataset file."""
    mock_open.return_value.__enter__.return_value = MagicMock(
        collection=MagicMock(return_value=[{"id": 1, "name": "item1"}, {"id": 2, "name": "item2"}])
    )

    runner = CliRunner()
    result = runner.invoke(preview_cli, ["show", "--name", "draft", "--collection", "collection1"])

    # Assertions
    assert result.exit_code == 0
    assert json.dumps({"id": 1, "name": "item1"}, indent=2) in result.output
    assert json.dumps({"id": 2, "name": "item2"}, indent=2) in result.output

    mock_locate.assert_called_once_with("draft")
    mock_open.assert_called_once_with("./dist/dataset-draft.dsh")


@patch("datafact.subcmd.preview.locate_draft_file", return_value="./dist/dataset-draft.dsh")
@patch("os.path.exists", return_value=False)
def test_preview_collection_file_not_found(mock_exists, mock_locate):
    """Test preview_collection command when the dataset file is not found."""
    runner = CliRunner()
    result = runner.invoke(preview_cli, ["show", "--name", "draft", "--collection", "collection1"])

    # Assertions
    assert result.exit_code == 1
    assert "draft file not found at ./dist/dataset-draft.dsh" in result.output

    mock_locate.assert_called_once_with("draft")


@patch("datafact.subcmd.preview.locate_draft_file", return_value="./dist/dataset-draft.dsh")
@patch("datafact.subcmd.preview.dataset_sh.open_dataset_file")
def test_list_collections_success(mock_open, mock_locate):
    """Test list_collections command with a valid dataset file."""
    mock_open.return_value.__enter__.return_value = MagicMock(
        collections=MagicMock(return_value=["collection1", "collection2"])
    )

    runner = CliRunner()
    result = runner.invoke(preview_cli, ["collections", "--name", "draft"])

    # Assertions
    assert result.exit_code == 0
    assert "Find 2 collections:" in result.output
    assert "01: collection1" in result.output
    assert "02: collection2" in result.output

    mock_locate.assert_called_once_with("draft")
    mock_open.assert_called_once_with("./dist/dataset-draft.dsh")
