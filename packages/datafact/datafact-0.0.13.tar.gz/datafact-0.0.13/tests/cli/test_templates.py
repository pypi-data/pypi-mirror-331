import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from datafact.cli import cli


@pytest.fixture
def mock_fact_templates():
    """Fixture to mock fact_templates."""
    return [
        MagicMock(name="Template 1", description="Description for template 1"),
        MagicMock(name="Template 2", description="Description for template 2"),
    ]


@patch("datafact.subcmd.templates.fact_templates")
def test_templates_cli(mock_templates, mock_fact_templates):
    """Test the templates_cli command."""
    mock_templates.__iter__.return_value = iter(mock_fact_templates)

    runner = CliRunner()
    result = runner.invoke(cli, ['templates'])

    # Assert command succeeded
    assert result.exit_code == 0

    # Assert the output contains the expected content
    assert "Available templates:" in result.output
    for idx, template in enumerate(mock_fact_templates, start=1):
        assert f"{idx:02}: {template.name}" in result.output
        assert template.description in result.output

    assert "--EOF--" in result.output
