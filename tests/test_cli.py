import contextlib
import os
import pathlib

import pytest
from typer.testing import CliRunner

from run_if.cli import app


@contextlib.contextmanager
def working_dir(path):
    old_path = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_path)


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0

    assert "Usage: run-if" in result.stdout


def test_cli_simple_command():
    runner = CliRunner()
    with runner.isolated_filesystem():
        assert not pathlib.Path(".run-if.json").exists()
        pathlib.Path("dep.txt").write_text("")
        result = runner.invoke(
            app, ["dep.txt", "==", "touch", "target.txt", "==", "target.txt"]
        )
        assert pathlib.Path(".run-if.json").exists()
        assert pathlib.Path("dep.txt").exists()
        assert result.exit_code == 0
        assert pathlib.Path("target.txt").exists()
        assert result.stdout == ""

        result = runner.invoke(
            app, ["dep.txt", "==", "touch", "target.txt", "==", "target.txt"]
        )
        assert result.exit_code == 1
        assert result.stdout == ""


def test_cli_missing_dependency_error():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            app, ["missing", "==", "touch", "target.txt", "==", "target.txt"]
        )
        assert result.exit_code == 3
        assert "Cannot compute hash for" in result.stdout


def test_cli_missing_target_causes_run_every_time():
    runner = CliRunner()
    with runner.isolated_filesystem():
        pathlib.Path("dep.txt").write_text("")
        result = runner.invoke(
            app, ["dep.txt", "==", "touch", "target.txt", "==", "target.txt", "missing"]
        )
        assert result.exit_code == 0

        result = runner.invoke(
            app, ["dep.txt", "==", "touch", "target.txt", "==", "target.txt", "missing"]
        )
        assert result.exit_code == 0


def test_cli_missing_no_dependencies():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["==", "touch", "target.txt", "==", "target.txt"])
        assert result.exit_code == 0

        result = runner.invoke(app, ["==", "touch", "target.txt", "==", "target.txt"])
        assert result.exit_code == 1
