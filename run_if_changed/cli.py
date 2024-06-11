import argparse
import json
import pathlib
import subprocess
import typing

import rich
import typer

from .change_detection import *

app = typer.Typer()
console = rich.console.Console()


CMD_SEP = "=="  # unfortunately, using -> causes problems with the shells...
DB_NAME = ".run-if.json"


@app.command()
def run_if(arguments: typing.List[str]):
    dependencies_command_targets = [[], [], []]

    # load the database (just a dict)
    DB_PATH = pathlib.Path(DB_NAME)
    if not DB_PATH.exists():
        DB_PATH.write_text("{}")
    db = json.loads(DB_PATH.read_text())
    for section in ["dependency hashes", "exit codes"]:
        if section not in db:
            db[section] = {}

    # sort the arguments
    current_type = 0
    for a in arguments:
        if a.strip() == CMD_SEP:
            current_type += 1
            if current_type > 2:
                print(
                    f"Too many '{CMD_SEP}' found in argument list. There should only be two."
                )
                raise typer.Exit(2)
            continue
        dependencies_command_targets[current_type].append(a)

    # we assume that the command should not be run
    # because it is obviously expensive (if it wasn't you would not need us).
    run_command = False
    # convince us that it _does_ need to run...

    # check for missing targets
    for t in [pathlib.Path(a) for a in dependencies_command_targets[2]]:
        if not t.exists():
            run_command = True
            break

    # check for changed dependencies
    # do determine if a dependency has changed, we compute its hash
    # and compare it to the last time we ran.
    # BUT, we only want to compare to the last time we ran _this_ command,
    # that way we can run several command in a row with the same
    # dependencies and they will all run.
    command_hash = md5sum((" ".join(dependencies_command_targets[1])).encode())
    if command_hash not in db["dependency hashes"]:
        db["dependency hashes"][command_hash] = {}
    dep_hashes = db["dependency hashes"][command_hash]
    for dep in [pathlib.Path(a) for a in dependencies_command_targets[0]]:
        _hash = compute_hash(dep)

        if dep_hashes.get(str(dep), None) != _hash:
            run_command = True
        dep_hashes[str(dep)] = _hash

    # write updated hashes back to disk
    DB_PATH.write_text(json.dumps(db))

    # run command if needed
    if run_command:
        try:
            results = subprocess.run(dependencies_command_targets[1])
            raise typer.Exit(results.returncode)
        except FileNotFoundError as e:
            print(f"Error running command: {e}")
            raise typer.Exit(127)

    raise typer.Exit(0)
