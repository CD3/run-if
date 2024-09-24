import contextlib
import os
import pathlib

import pytest

from run_if_changed.change_detection import *


@contextlib.contextmanager
def working_dir(path):
    old_path = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_path)


def test_get_files_in_directory(tmp_path):
    with working_dir(tmp_path):
        pathlib.Path("dir").mkdir()
        pathlib.Path("dir/l1").mkdir()
        pathlib.Path("dir/m1").mkdir()
        pathlib.Path("dir/n1").mkdir()
        pathlib.Path("dir/dep.txt").write_text("")
        pathlib.Path("dir/l1/l2").mkdir()
        pathlib.Path("dir/l1/dep.txt").write_text("")
        pathlib.Path("dir/l1/l2/l3").mkdir()
        pathlib.Path("dir/n1/dep").write_text("")

        pathlib.Path("dir/l1/l2/l3/m1").symlink_to(
            pathlib.Path("dir/m1").absolute(), target_is_directory=True
        )
        pathlib.Path("dir/m1/l1").symlink_to(
            pathlib.Path("dir/l1").absolute(), target_is_directory=True
        )

        pathlib.Path("dir/m1/n1").symlink_to(
            pathlib.Path("dir/n1").absolute(), target_is_directory=True
        )

        assert len((list(get_all_files(pathlib.Path("dir/l1"))))) == 3
