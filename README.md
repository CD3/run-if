# `run-if` - conditionally execute command if targets don't exist or dependencies have changed.

This is a simple but powerful tool for conditionally executing commands similar to `checkexec`
(https://github.com/kurtbuilds/checkexec), but it uses a hash of the
contents of the dependencies to detect when a dependency has actually changed (similar to
[doit](https://pydoit.org/)). It also supports directories as dependencies,
multiple targets, and sentinal files. As with `checkexec`, it pairs well with `just`
(https://github.com/casey/just). For me, using `run-if` with `just` is simpler
than `doit` and more powerful than using `checkexec` with `just`.

Originally, `run-if` was written in Python but was then rewritten in Rust as a way for me to learn Rust. The
Python version sill works, although it does tend to run slow on large directory dependencies. When I rewrote it in Rust, I expected
it to run much faster, but it actually ended up running _slower_. The problem turned out to be the hash function implementation.
Python's `hashlib` module uses openssl and the hash function I was using in Rust was written in Rust, which was slower. Switching
to the `openssl` crate fixed the issue.

The Rust version is now quite a bit faster than the Python version but only because of a few optimizations that
could have also been implemented in the Python version.

**Update** I had a student recommend using Blake3 for the hash function which is faster than md5. The
Rust version is now much faster than the Python version and does not depend on OpenSSL.

Here's what it looks like...

```bash
$ run-if -d main.cpp -t main -- g++ main.cpp -o main
```

If `main` does not exist, or if the contents of `main.cpp` have changed since the last time `run-if` was called (with this command),
`g++ main.cpp -o main` will be run.
Multiple targets can be listed and both targets and dependencies can be files or directories.

```bash
$ run-if -d src/ -t build/test1 -t build/test2 build/data/ -- cmake --build build
```

You can also give dependencies, the command, and targets in _argument groups_. Argument groups are arguments separated by a group delimiter '=='.
For example:

```bash
$ run-if -- main.cpp == g++ main.cpp -o main == main
```

Here, `main.cp` is a dependency for the command `g++ main.cpp -o main` and `main` is a target. This syntax is useful for giving dependencies using shell globs.
Note that the `--` here is necessary to allow options in the command to be executed (`-o` here).

## Features

- Simple. It does one thing and that's it.
- Supports multiple targets. If any of the targets do not exists, the command will be executed.
- Supports sentinal files. If any of the sentinals exists, the command will be executed (useful for cleaning tasks).
- Command runs if dependencies have _changed_, not _updated_. `run-if` compares a hash of each dependency to its hash the last time it ran to determine if a dependency has changed.
- Supports directories as dependencies. Rather than listing every file in a directory as a dependency, `run-if` allows directories to be dependencies. If any file in the directory has changed, or if any files have been added or removed, the command will be ran.
- Support for executing command if previous run failed. With the `--run-until-success` option, `run-if` will execute the command if the last run returned a non-zero exit code.

## Install

```bash
cargo install --git https://github.com/CD3/run-if.git
```

## Concepts

`run-if` is a tool for executing commands if certain conditions are met. Several different types of files/directories are considered when
determining if a command should run.

targets
: Files or directories that will cause the command to run if they are _**not** present_.

dependencies
: Files or directories that will cause the command to run if they _change_.

sentinals
: Files or directories that will cause the command to run if they _**do** exist_.



### Rules for determining if a command will be run

`run-if` does not compare the modification times of dependencies and targets to determine if a command should be run. Instead, it writes a small JSON
file in the current working directory to cache information between runs that is used to determine if a command should run
(it does use modification times as an optimization to determine if the file contents need to be checked).

The first time `run-if` is called, it computes a hash of all dependencies and caches these in the JSON file.
The next time it runs, it computes the hash of all dependencies that have been "modifed" (updated mtime) and
compares them to the cached hashes to decide if the command should be executed.
Dependency hashes for different commands are stored separately.
If `run-if` is called with the same dependency but different commands, both commands may run.

If a command is executed, the exit status of the command is also cached. This can be used to then decide if the command should be executed in the future (see below).

The rules for determining if a command will be ran are as follows:

- By default, assume the command should _not_ be run.
- If _any_ targets are missing, run the command.
- If the hash of dependencies differ from the previous run (of the same command), run the command.
- If the `--run-until-success` option has been given and the command returned a non-zero exit status on the previous run, run the command.

Note that these rules lead to a few properties:

- Listing a target that does not exist and will not be created by the command will cause a command to always run.
- Listing no targets will cause all commands with the same dependencies to run one, and then not again until the dependencies change.
- If a command has no targets or dependencies, it will not be executed.

## Usage


`run-if` supports two methods for specifying dependencies and targets. The first version (written in python) used "argument groups" to identify dependencies, the command, and targets:


```bash
$ run-if -- dep1.txt -d dep2.txt == cmake --build . == build/a.out 
```

Argument groups are separated by `==`. The first set of arguments are dependencies, the second set are the command, and the thrid set are teh targets. The idea was that
dependencies feed into the command which creates the targets. Originally I used `->` instead of `==`, but it caused problems with argument parsing and shell redirection.

`run-if` also supports dependencies and targets given as options:

```bash
$ run-if -d dep1.txt -d dep2.txt -t build/a.out -- cmake --build .
```

Another useful (and unique) option is `--trye-until-success`:

```bash
$ run-if --try-until-sucess -d dep1.txt -d dep2.txt -t build/a.out -- cmake --build .
```

The `--try-until-success` will cause the command to be executed if the last run did not succeed (returned non-zero exit code).
It has been useful for my development workflow. I run a build-and-test command in a terminal with `just` and `entr` while editing
code in Neovim. If I run into a compile error, I can run the build-and-test command in Neovim using [:AsyncRun](https://github.com/skywind3000/asyncrun.vim)
and jump to the source location of the compiler error. Without the option, `run-if` would not re-run the build-and-test command after finished in the
terminal unless a source file changed (not just saved).

### Examples

Run Conan if the projects `conanfile.txt` files changes

```bash
$ run-if --dependency conanfile.txt -- conan install . --build missing
```
Note that the `--` is required to allow passing options to the `conan` command.

Run CMake if the cache file has not been created or the CMakeLists.txt file has changed
```bash
$ run-if --dependency CMakeLists.txt --target build/CMakeCache.txt -- bash -c 'cd build && cmake ..'
```

Run a `make clean` if the build directory exists
```bash
$ run-if --sentinal build -- make clean
```
