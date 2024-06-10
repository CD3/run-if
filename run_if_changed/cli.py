import argparse
import json
import pathlib
import subprocess
import typing

import rich
import typer

app = typer.Typer()
console = rich.console.Console()


CMD_SEP = "=="  # unfortunately, using -> causes problems with the shells...
DB_NAME = ".run-if.json"


def compute_hash(path: pathlib.Path):
    if path.is_file():
        return (
            subprocess.check_output(f"md5sum {path}", shell=True)
            .decode()
            .split()[0]
            .strip()
        )
    if path.is_dir():
        return (
            subprocess.check_output(
                f"find {path} -type f | xargs md5sum | gawk '{{print $1}}' | md5sum",
                shell=True,
            )
            .decode()
            .split()[0]
            .strip()
        )

    print(f"Cannot compute hash for '{path}'. It is not a file or directory.")
    raise typer.Exit(3)


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

    dep_hashes = json.loads(DB_PATH.read_text())
    for dep in [pathlib.Path(a) for a in dependencies_command_targets[0]]:
        _hash = compute_hash(dep)

        if dep_hashes.get(str(dep), None) != _hash:
            run_command = True
        dep_hashes[str(dep)] = _hash

    DB_PATH.write_text(json.dumps(dep_hashes))

    if run_command:
        subprocess.run(dependencies_command_targets[1])
        raise typer.Exit(0)

    raise typer.Exit(0)
