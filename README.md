# `run-if` - conditionally run command if targets don't exist or dependencies have changed.

This is a simple python script that bascially does what checkexec (https://github.com/kurtbuilds/checkexec), but it uses a hash
of the contents of the dependencies to decide if the command should be ran and supports multiple targets.

```bash
$ run-if main.cpp == g++ main.pp -o main == main
```

If `main` does not exist, or if the contents of `main.cpp` have changed since the last time it `run-if` was called,
the command will be run.

The syntax is different than checkexec
```bash
$ run-if [DEPENDENCY...] == <COMMAND> == [TARGET...]
```

Multiple targets can be listed and both targets and dependencies can be files or directories.

```bash
$ run-if -- src/ == cmake --build build == build/test1 build/test2 build/data/
```

Currently the hash of dependencies are being computed with shell commands using the `subprocess` module, so it will fail to run
if `md5sum` or `find` are missing, or if the default shell does not support pipes.


# Install

Install `run-if` with `pip` using the `run-if-changed` package (`run-if` is too similar to another prackage already in the repository).

```bash
$ pip install run-if-changed
```
