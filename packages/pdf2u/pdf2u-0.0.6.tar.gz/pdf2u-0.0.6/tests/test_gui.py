import subprocess
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from pdf2u.main import app as cli_app


@patch("subprocess.run")
def test_gui_command_default_args(mock_run):
    """Test that the gui command works with default arguments."""
    # Setup the mock to return a successful result
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

    runner = CliRunner()
    result = runner.invoke(cli_app, ["gui"])

    # Check the command executed successfully
    assert result.exit_code == 0

    # Verify subprocess.run was called once
    mock_run.assert_called_once()

    # Get the args passed to subprocess.run
    call_args = mock_run.call_args[0][0]

    # Verify basic structure of the command
    assert call_args[0] == "streamlit"
    assert call_args[1] == "run"
    assert Path(call_args[2]).name == "gui.py"
    assert "--server.port" in call_args
    assert "7860" in call_args  # Default port
    assert "--server.address" in call_args
    assert "0.0.0.0" in call_args  # Default address


@patch("subprocess.run")
def test_gui_command_custom_args(mock_run):
    """Test that the gui command works with custom arguments."""
    # Setup the mock to return a successful result
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

    runner = CliRunner()
    result = runner.invoke(
        cli_app, ["gui", "--port", "8501", "--address", "127.0.0.1", "--no-browser"]
    )

    # Check the command executed successfully
    assert result.exit_code == 0

    # Verify subprocess.run was called once
    mock_run.assert_called_once()

    # Get the args passed to subprocess.run
    call_args = mock_run.call_args[0][0]

    # Verify custom arguments were passed correctly
    assert "--server.port" in call_args
    assert "8501" in call_args
    assert "--server.address" in call_args
    assert "127.0.0.1" in call_args
    assert "--server.headless" in call_args
    assert "true" in call_args


@patch("subprocess.run")
def test_gui_command_exception(mock_run):
    """Test that exceptions are handled properly."""
    # Setup the mock to raise an exception
    mock_run.side_effect = Exception("Test error")

    runner = CliRunner()
    result = runner.invoke(cli_app, ["gui"])

    # Command should fail
    assert result.exit_code == 1
