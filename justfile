list:
  just --list

run-cargo-tests:
  cd tests/workspace && cargo test -- --test-threads 1

run-cram-tests:
  cd tests/cram && cram *.t

test: run-cargo-tests run-cram-tests

bench:
  cargo bench
