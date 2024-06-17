import fnmatch
import hashlib
import pathlib
import shutil
import subprocess

import typer

exclude_dirs = []
exclude_patterns = []


def exclude_path(p):
    """Return true if a path should be excluded from change detection."""
    parts = p.parts
    for d in exclude_dirs:
        if d in parts:
            return True
    for pat in exclude_patterns:
        if fnmatch.fnmatch(p, path):
            return True
    return False


def md5(byte_str):
    """Return the md5 hash of a byte string"""
    return hashlib.md5(byte_str).hexdigest()


hash_func = md5


def get_all_files(path: pathlib.Path, symlinks_followed=None):
    """
    Get a list of all files in a given directory. Uses pathlib.Path().rglob("*")
    to get the list of files but follows any symlinks that point to directories.
    """
    if symlinks_followed is None:
        symlinks_followed = []
    for file in filter(lambda p: not exclude_path(p), path.rglob("*")):
        if file.is_file():
            yield file.absolute()
        if file.is_symlink() and file.resolve().is_dir():
            if str(file.absolute()) not in symlinks_followed:
                symlinks_followed.append(str(file.absolute()))
                for f in get_all_files(file.resolve(), symlinks_followed):
                    yield f


def compute_hash(path: pathlib.Path):
    """Compue a hash for a file or directory that can be used to detect changes."""
    # if path ia a file, we just return the hash of its contents.
    # if it is a directory, we hash all of the file contents, then hash
    # the hashes joined together.

    if path.is_file() or (path.is_symlink() and path.resolve().is_file()):
        return hash_func(path.read_bytes())

    if path.is_dir() or (path.is_symlink() and path.resolve().is_dir()):
        # do we need to sort the files to make sure the order is always the same?
        _hash = hash_func(
            "".join(
                [hash_func(p.read_bytes()) + str(p) for p in get_all_files(path)]
            ).encode()
        )
        return _hash

    print(f"Cannot compute hash for '{path}'. It is not a file or directory.")
    raise typer.Exit(3)
