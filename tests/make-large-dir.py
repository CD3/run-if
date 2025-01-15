import argparse
import pathlib
import random

parser = argparse.ArgumentParser(
    description="Generate a large directory tree for testing run-if performance."
)

parser.add_argument("--levels", type=int, default=2)
parser.add_argument("--files-per-level", type=int, default=2)
parser.add_argument("--dirs-per-level", type=int, default=2)
parser.add_argument("--root-name", type=str, default="big_dir")
parser.add_argument(
    "--file-size", type=int, help="size of each file in bytes", default=2
)

args = parser.parse_args()


file_text = "a" * args.file_size


def make_dir(name: pathlib.Path, depth: int = 0):
    name.mkdir(exist_ok=True)
    if args.levels - depth <= 0:
        return
    for file in map(lambda i: f"f{i}", range(args.files_per_level)):
        f = name / file
        f.write_text(file_text)
    for directory in map(lambda i: f"d{i}", range(args.dirs_per_level)):
        d = name / directory
        make_dir(d, depth + 1)


make_dir(
    pathlib.Path(
        f"{args.root_name}-{args.levels}-{args.files_per_level}-{args.dirs_per_level}-{args.file_size}"
    )
)
