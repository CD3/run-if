import pathlib


def task_run_it():
    yield {
        "name": "command 1",
        "file_dep": ["deps/one.txt"],
        "actions": ['echo "command 1"'],
    }
    yield {
        "name": "command 2",
        "file_dep": ["deps/one.txt", "deps/two.txt"],
        "actions": ['echo "command 2"'],
    }
    yield {
        "name": "command 3",
        "file_dep": list(
            filter(lambda p: p.is_file(), pathlib.Path("deps").rglob("*"))
        ),
        "actions": ['echo "command 3"'],
    }
    yield {
        "name": "command 4",
        "file_dep": list(
            filter(lambda p: p.is_file(), pathlib.Path("deps").rglob("*"))
        ),
        "actions": ['echo "command 3"'],
    }
