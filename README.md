# `run-if` - conditionally run command if targets don't exist or dependencies have changed.

This is a simple python script that basically does what `checkexec` (https://github.com/kurtbuilds/checkexec) does, but it uses a hash
of the contents of the dependencies to decide if the command should be run
(similar to [doit](https://pydoit.org/)). It also supports directories as
dependencies and multiple targets. As with `checkexec`, it pairs well with
`just` (https://github.com/casey/just). For me, using `run-it` with `just` is simpler
than `doit` and more powerful than using `checkexec` with `just`.

```bash
$ run-if main.cpp == g++ main.cpp -o main == main
```

If `main` does not exist, or if the contents of `main.cpp` have changed since the last time `run-if` was called,
`g++ main.cpp -o main` will be run.

The syntax is different than checkexec:
```bash
$ run-if [DEPENDENCY...] == <COMMAND> == [TARGET...]
```
Originally I tried using "->" instead of "==" to give a visual of "dependencies to into a command that produces targets", but
it caused problems with the option parser and the shell (the option parser treated '-' as an option indicator and the shell
treated '>' as a file redirect).

Multiple targets can be listed and both targets and dependencies can be files or directories.

```bash
$ run-if -- src/ == cmake --build build == build/test1 build/test2 build/data/
```

## Features

- It is simple, it does one thing and that's it.
- Supports multiple targets. If a command is expected to produce multiple targets but fails after creating the first, it will be run the next time.
- Command runs if dependencies have _changed_, not _updated_. `run-if` compares a hash of each dependency to its hash the last time it ran to determine if a dependency has changed.
- Supports directories as dependencies. Rather than listing every file in a directory as a dependency, `run-if` allows directories to be dependencies. If any file in the directory has changed, or if any files have been added or removed, the command will be ran.

## Install

Install `run-if` with `pip` using the `run-if-changed` package (`run-if` is too similar to another package already in the repository).

```bash
$ pip install run-if-changed
```

## Rules for determining if a command will be run

`run-if` does not use modification times to determine if a command should be run. Instead, it writes a small JSON
file in the current working directory to cache information between runs that is used to determine if a command should run.
Every time `run-if` is called, it computes a hash of all dependencies and caches these in the JSON file. However, dependency hashes
for different commands are stored separately. If `run-if` is called with the same dependency but different commands, both commands may run.

If a command is ran, the exit status of the command is also cached. This can be used to then decide if the command should be ran in the future (see below).

The rules for determining if a command will be ran are as follows:

- By default, assume the command should _not_ be run.
- If _any_ targets are missing, run the command.
- If the hash of dependencies differ from the previous run (of the same command), run the command.
- If the `--run-until-success` option has been given and the command returned a non-zero exit status on the previous run, run the command.

Note that these rules lead to a few properties:

- Listing a target that does not exist and will not be created by the command will cause a command to always run.
- Listing no targets will cause all commands with the same dependencies to run one, and then not again until the dependencies change.
- If a command has no targets or dependencies, it will not be ran.

The `--run-until-success` is useful for my development workflow. I run a build-and-test command in a terminal with `just` and `entr` while editing
code in Neovim. If I run into a compile error, I can run the build-and-test command in Neovim using [:AsyncRun](https://github.com/skywind3000/asyncrun.vim)
and jump to the source location of the compiler error. Without the option, `run-if` would not re-run the build-and-test command after finished in the
terminal unless a source file changed (not just saved).
