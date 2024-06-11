import hashlib
import pathlib
import subprocess

import typer


def md5sum(text):
    """Return the md5sum of a text string"""
    return hashlib.md5(text).hexdigest()


def compute_hash(path: pathlib.Path):
    """Compue a hash for a file or directory that can be used to detect changes."""
    # we are currently relying on command-line utils to compute the hash.
    # for a file, we return the md5sum of its contents.
    # for a directory, we compute the md5sum of all files and then compute
    # the md5sum of thier sums.
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
                f"find {path} -type f | xargs md5sum | md5sum",
                shell=True,
            )
            .decode()
            .split()[0]
            .strip()
        )

    print(f"Cannot compute hash for '{path}'. It is not a file or directory.")
    raise typer.Exit(3)
