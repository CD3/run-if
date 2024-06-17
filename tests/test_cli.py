import contextlib
import os
import pathlib

import pytest
from typer.testing import CliRunner

from run_if_changed.cli import app


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
        assert result.exit_code == 0
        assert result.stdout == ""

        result = runner.invoke(
            app, ["dep.txt", "==", "touch", "target2.txt", "==", "target.txt"]
        )
        assert result.exit_code == 0
        assert result.stdout == ""
        assert pathlib.Path("target2.txt").exists()


def test_cli_changing_dep_file_cause_rerun():
    runner = CliRunner()
    with runner.isolated_filesystem():
        pathlib.Path("dep.txt").write_text("")
        result = runner.invoke(app, ["dep.txt", "==", "echo", "HI"])
        assert result.exit_code == 0
        assert result.stdout == "HI\n"

        result = runner.invoke(app, ["dep.txt", "==", "echo", "HI"])
        assert result.exit_code == 0
        assert result.stdout == ""

        pathlib.Path("dep.txt").write_text("1")
        result = runner.invoke(app, ["dep.txt", "==", "echo", "HI"])
        assert result.exit_code == 0
        assert result.stdout == "HI\n"

        pathlib.Path("dir").mkdir()
        result = runner.invoke(app, ["dir", "==", "echo", "HI"])
        assert result.exit_code == 0
        assert result.stdout == "HI\n"

        result = runner.invoke(app, ["dir", "==", "echo", "HI"])
        assert result.exit_code == 0
        assert result.stdout == ""

        pathlib.Path("dir/dep.txt").write_text("1")
        result = runner.invoke(app, ["dir", "==", "echo", "HI"])
        assert result.exit_code == 0
        assert result.stdout == "HI\n"


def test_cli_call_with_no_targets():
    runner = CliRunner()
    with runner.isolated_filesystem():
        assert not pathlib.Path(".run-if.json").exists()
        pathlib.Path("dep.txt").write_text("")
        result = runner.invoke(app, ["dep.txt", "==", "touch", "target.txt"])
        assert pathlib.Path(".run-if.json").exists()
        assert pathlib.Path("dep.txt").exists()
        assert result.exit_code == 0
        assert pathlib.Path("target.txt").exists()
        assert result.stdout == ""

        result = runner.invoke(app, ["dep.txt", "==", "touch", "target2.txt"])
        assert result.exit_code == 0
        assert result.stdout == ""
        assert pathlib.Path("target2.txt").exists()


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
        assert result.exit_code == 0


def test_cli_command_typo():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["==", "toch", "target.txt", "==", "target.txt"])
        assert result.exit_code == 127


def test_run_until_sucess():
    runner = CliRunner()
    with runner.isolated_filesystem():
        pathlib.Path("dep.txt").write_text("")
        result = runner.invoke(
            app,
            [
                "--run-until-success",
                "--",
                "dep.txt",
                "==",
                "bash",
                "-c",
                "date +%N > date.txt && echo HI",
            ],
        )

        assert result.exit_code == 0
        assert result.stdout == "HI\n"

        orig_date_text = pathlib.Path("date.txt").read_text()

        result = runner.invoke(
            app,
            [
                "--run-until-success",
                "--",
                "dep.txt",
                "==",
                "bash",
                "-c",
                "date +%N > date.txt && echo HI",
            ],
        )
        assert result.exit_code == 0
        assert result.stdout == ""
        new_date_text = pathlib.Path("date.txt").read_text()
        assert orig_date_text == new_date_text

        result = runner.invoke(
            app,
            [
                "--run-until-success",
                "--",
                "dep.txt",
                "==",
                "bash",
                "-c",
                "date +%N > date.txt && ech HI",
            ],
        )

        assert result.exit_code == 127
        assert result.stdout == "bash: line 1: ech: command not found\n"

        orig_date_text = pathlib.Path("date.txt").read_text()

        result = runner.invoke(
            app,
            [
                "--run-until-success",
                "--",
                "dep.txt",
                "==",
                "bash",
                "-c",
                "date +%N > date.txt && ech HI",
            ],
        )
        assert result.exit_code == 127
        assert result.stdout == "bash: line 1: ech: command not found\n"
        new_date_text = pathlib.Path("date.txt").read_text()
        assert orig_date_text != new_date_text


def test_deps_and_targets_as_options():
    runner = CliRunner()
    with runner.isolated_filesystem():
        pathlib.Path("dep.txt").write_text("")
        result = runner.invoke(
            app,
            [
                "--run-until-success",
                "--dependency",
                "dep.txt",
                "--target",
                "date.txt",
                "--",
                "bash",
                "-c",
                "date +%N > date.txt && echo HI",
            ],
        )
        assert result.stdout == "HI\n"
        assert result.exit_code == 0

        result = runner.invoke(
            app,
            [
                "--run-until-success",
                "--dependency",
                "dep.txt",
                "--target",
                "date.txt",
                "--",
                "bash",
                "-c",
                "date +%N > date.txt && echo HI",
            ],
        )
        assert result.stdout == ""
        assert result.exit_code == 0

        pathlib.Path("dep.txt").write_text("1")
        result = runner.invoke(
            app,
            [
                "--run-until-success",
                "--dependency",
                "dep.txt",
                "--target",
                "date.txt",
                "--",
                "bash",
                "-c",
                "date +%N > date.txt && echo HI",
            ],
        )
        assert result.stdout == "HI\n"
        assert result.exit_code == 0


def test_missing_option_and_arg_deps_and_targets():
    runner = CliRunner()
    with runner.isolated_filesystem():
        pathlib.Path("dep1.txt").write_text("")
        pathlib.Path("dep2.txt").write_text("")
        result = runner.invoke(
            app,
            [
                "--run-until-success",
                "--dependency",
                "dep1.txt",
                "--target",
                "date1.txt",
                "--",
                "dep2.txt",
                "==",
                "bash",
                "-c",
                "date +%N > date1.txt && echo HI",
                "==",
                "date2.txt",
            ],
        )
        assert result.stdout == "HI\n"
        assert result.exit_code == 0

        result = runner.invoke(
            app,
            [
                "--run-until-success",
                "--dependency",
                "dep1.txt",
                "--target",
                "date1.txt",
                "--",
                "dep2.txt",
                "==",
                "bash",
                "-c",
                "date +%N > date1.txt && echo HI",
                "==",
                "date2.txt",
            ],
        )
        assert result.stdout == "HI\n"
        assert result.exit_code == 0

        pathlib.Path("date2.txt").write_text("")
        result = runner.invoke(
            app,
            [
                "--run-until-success",
                "--dependency",
                "dep1.txt",
                "--target",
                "date1.txt",
                "--",
                "dep2.txt",
                "==",
                "bash",
                "-c",
                "date +%N > date1.txt && echo HI",
                "==",
                "date2.txt",
            ],
        )
        assert result.stdout == ""
        assert result.exit_code == 0

        pathlib.Path("dep1.txt").write_text("1")
        result = runner.invoke(
            app,
            [
                "--run-until-success",
                "--dependency",
                "dep1.txt",
                "--target",
                "date1.txt",
                "--",
                "dep2.txt",
                "==",
                "bash",
                "-c",
                "date +%N > date1.txt && echo HI",
                "==",
                "date2.txt",
            ],
        )
        assert result.stdout == "HI\n"
        assert result.exit_code == 0

        result = runner.invoke(
            app,
            [
                "--run-until-success",
                "--dependency",
                "dep1.txt",
                "--target",
                "date1.txt",
                "--",
                "dep2.txt",
                "==",
                "bash",
                "-c",
                "date +%N > date1.txt && echo HI",
                "==",
                "date2.txt",
            ],
        )
        assert result.stdout == ""
        assert result.exit_code == 0

        pathlib.Path("dep2.txt").write_text("1")
        result = runner.invoke(
            app,
            [
                "--run-until-success",
                "--dependency",
                "dep1.txt",
                "--target",
                "date1.txt",
                "--",
                "dep2.txt",
                "==",
                "bash",
                "-c",
                "date +%N > date1.txt && echo HI",
                "==",
                "date2.txt",
            ],
        )
        assert result.stdout == "HI\n"
        assert result.exit_code == 0

        result = runner.invoke(
            app,
            [
                "--run-until-success",
                "--dependency",
                "dep1.txt",
                "--target",
                "date1.txt",
                "--",
                "dep2.txt",
                "==",
                "bash",
                "-c",
                "date +%N > date1.txt && echo HI",
                "==",
                "date2.txt",
            ],
        )
        assert result.stdout == ""
        assert result.exit_code == 0

        result = runner.invoke(
            app,
            [
                "--run-until-success",
                "--dependency",
                "dep1.txt",
                "--dependency",
                "dep2.txt",
                "--target",
                "date1.txt",
                "--target",
                "date2.txt",
                "--",
                "bash",
                "-c",
                "date +%N > date1.txt && echo HI",
            ],
        )
        assert result.stdout == ""
        assert result.exit_code == 0

        pathlib.Path("dep2.txt").write_text("")

        result = runner.invoke(
            app,
            [
                "--run-until-success",
                "--dependency",
                "dep1.txt",
                "--dependency",
                "dep2.txt",
                "--target",
                "date1.txt",
                "--target",
                "date2.txt",
                "--",
                "bash",
                "-c",
                "date +%N > date1.txt && echo HI",
            ],
        )
        assert result.stdout == "HI\n"
        assert result.exit_code == 0


def test_sentinals():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            app,
            [
                "--sentinal",
                "sent1.txt",
                "--",
                "==",
                "bash",
                "-c",
                "date +%N > date1.txt && echo HI",
                "==",
            ],
        )
        assert result.stdout == ""
        assert result.exit_code == 0

        pathlib.Path("sent1.txt").write_text("")
        result = runner.invoke(
            app,
            [
                "--sentinal",
                "sent1.txt",
                "--",
                "==",
                "bash",
                "-c",
                "date +%N > date1.txt && echo HI",
                "==",
            ],
        )
        assert result.stdout == "HI\n"
        assert result.exit_code == 0


def test_dry_run():
    runner = CliRunner()
    with runner.isolated_filesystem():
        pathlib.Path("dep.txt").write_text("")
        result = runner.invoke(
            app,
            [
                "--dry-run",
                "--",
                "dep.txt",
                "==",
                "touch",
                "target.txt",
                "==",
                "target.txt",
            ],
        )

        assert "Checking targets:" in result.stdout
        assert "Checking sentinals:" in result.stdout
        assert "Checking dependencies:" in result.stdout
        assert "'target.txt' does NOT exist, command will be run." in result.stdout
        assert "no hashes in the cache for command." in result.stdout
        assert "Exit status of previous run is being ignored" in result.stdout
        assert result.exit_code == 0

        result = runner.invoke(
            app,
            [
                "--dry-run",
                "--",
                "dep.txt",
                "==",
                "touch",
                "target.txt",
                "==",
                "target.txt",
            ],
        )

        assert "Checking targets:" in result.stdout
        assert "Checking sentinals:" in result.stdout
        assert "Checking dependencies:" in result.stdout
        assert "'target.txt' does NOT exist, command will be run." in result.stdout
        assert "no hashes in the cache for command." in result.stdout
        assert "Exit status of previous run is being ignored" in result.stdout
        assert result.exit_code == 0

        result = runner.invoke(
            app, ["--", "dep.txt", "==", "touch", "target.txt", "==", "target.txt"]
        )

        result = runner.invoke(
            app,
            [
                "--dry-run",
                "--",
                "dep.txt",
                "==",
                "touch",
                "target.txt",
                "==",
                "target.txt",
            ],
        )

        assert "Checking targets:" in result.stdout
        assert "Checking sentinals:" in result.stdout
        assert "Checking dependencies:" in result.stdout
        assert "'target.txt' exists." in result.stdout
        assert "hash for 'dep.txt' matches cache." in result.stdout
        assert "Exit status of previous run is being ignored" in result.stdout
        assert result.exit_code == 0
