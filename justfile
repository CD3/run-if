list:
  just --list

test:
  cd tests/workspace && cargo test -- --test-threads 1
  cd tests/cram && cram *.t


bench:
  cargo bench
