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

    DB_PATH = pathlib.Path(DB_NAME)
    if not DB_PATH.exists():
        DB_PATH.write_text("{}")

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

    run_command = False
    for t in [pathlib.Path(a) for a in dependencies_command_targets[2]]:
        if not t.exists():
            run_command = True
            break

    # load list of previous hashes
    db = json.loads(DB_PATH.read_text())
    for section in ["dependency hashes", "exit codes"]:
        if section not in db:
            db[section] = {}

    dep_hashes = db["dependency hashes"]
    for dep in [pathlib.Path(a) for a in dependencies_command_targets[0]]:
        _hash = compute_hash(dep)

        if dep_hashes.get(str(dep), None) != _hash:
            run_command = True
        dep_hashes[str(dep)] = _hash

    # write updated hashes back to disk
    DB_PATH.write_text(json.dumps(db))

    if run_command:
        try:
            results = subprocess.run(dependencies_command_targets[1])
            raise typer.Exit(results.returncode)
        except FileNotFoundError as e:
            print(f"Error running command: {e}")
            raise typer.Exit(127)

    raise typer.Exit(0)
