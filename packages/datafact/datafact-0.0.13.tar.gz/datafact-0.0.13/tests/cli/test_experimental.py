import pytest
from click.testing import CliRunner
from src.datafact.subcmd.experimental import experimental_cli


def test_experimental_cli_runs_without_arguments():
    runner = CliRunner()
    result = runner.invoke(experimental_cli)
    assert result.exit_code == 0
    assert "experimental features." in result.output


def test_experimental_cli_help_option():
    runner = CliRunner()
    result = runner.invoke(experimental_cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "experimental features." in result.output
