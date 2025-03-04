import pytest
from click.testing import CliRunner
from git_commit_chart.app import main

@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()

def test_cli_default_options(runner):
    """Test CLI with default options."""
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'Run the Git Commit Chart application' in result.output

def test_cli_development_mode(runner):
    """Test CLI in development mode."""
    result = runner.invoke(main, ['--port', '5000', '--host', '127.0.0.1', '--test-mode'])
    assert result.exit_code == 0
    assert '127.0.0.1' in result.output
    assert '5000' in result.output
    assert 'development mode' in result.output.lower()

def test_cli_production_mode(runner):
    """Test CLI in production mode."""
    result = runner.invoke(main, ['--production', '--test-mode'])
    assert result.exit_code == 0
    assert 'production mode' in result.output.lower()

def test_cli_custom_port(runner):
    """Test CLI with custom port."""
    result = runner.invoke(main, ['--port', '8080', '--test-mode'])
    assert result.exit_code == 0
    assert '8080' in result.output

def test_cli_custom_host(runner):
    """Test CLI with custom host."""
    result = runner.invoke(main, ['--host', '0.0.0.0', '--test-mode'])
    assert result.exit_code == 0
    assert '0.0.0.0' in result.output 