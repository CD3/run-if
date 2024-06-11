# `run-if` - conditionally run command if targets don't exist or dependencies have changed.

This is a simple python script that bascially does what checkexec (https://github.com/kurtbuilds/checkexec) does, but it uses a hash
of the contents of the dependencies to decide if the command should be run, and supports directories as dependencies and multiple targets.

```bash
$ run-if main.cpp == g++ main.cpp -o main == main
```

If `main` does not exist, or if the contents of `main.cpp` have changed since the last time `run-if` was called,
`g++ main.cpp -o main` will be run.

The syntax is different than checkexec:
```bash
$ run-if [DEPENDENCY...] == <COMMAND> == [TARGET...]
```

Multiple targets can be listed and both targets and dependencies can be files or directories.

```bash
$ run-if -- src/ == cmake --build build == build/test1 build/test2 build/data/
```

Currently, the hash of dependencies are being computed with shell commands using the `subprocess` module, so it will fail to run
if `md5sum` or `find` are missing, or if the default shell does not support pipes.

## Features

- It is simple, it does one thing.
- Supports multiple targets. If a command is expected to produce multiple targets but fails after creating the first, it will be run the next time.
- Command runs if dependencies have _changed_, not _updated_. `run-if` compares a hash of each dependency to its hash the last time it ran to determine if a dependency has changed.
- Supports directories as dependencies. Rather than listing every file in a directory as a dependency, `run-if` allows directories to be dependencies. If any file in the directory has changed, or if any files have been added or removed, the command will be ran.

## Install

Install `run-if` with `pip` using the `run-if-changed` package (`run-if` is too similar to another package already in the repository).

```bash
$ pip install run-if-changed
```
