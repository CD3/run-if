export PATH := x"${HOME}/.local/bin" + ":" + x"${HOME}/.cargo/bin" + ":" + justfile_directory() / ".rustenv/rust/bin" + x":${PATH}"

list:
    just --list

check-tools:
    bash scripts/check-tools

provision: check-tools
    #! /bin/bash
    test -e .venv || uv venv
    test -e .venv/bin/conan || uv pip install cram

build TYPE="debug":
    #! /bin/bash
    if [ "{{ TYPE }}" == "debug" ]; then
      cargo build
      exit 0
    fi
    if [ "{{ TYPE }}" == "release" ]; then
      cargo build --release
      exit 0
    fi
    echo "Unknown build configuation '{{ TYPE }}'."
    exit 1

run-cargo-tests:
    cd tests/workspace && cargo test -- --test-threads 1

run-cram-tests TYPE="debug": (build TYPE)
    #! /bin/bash
    export CLI_EXE="${PWD}/target/{{ TYPE }}/run-if"
    uv run cram tests/cram/*.t

test: run-cargo-tests (run-cram-tests "debug") (run-cram-tests "release")

bench:
    cargo bench
