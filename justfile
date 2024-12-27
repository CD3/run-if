set positional-arguments

test: test-pytest test-cram

test-pytest *args:
        uv run pytest "$@"
test-cram *args:
        uv run cram --shell /bin/bash "$@" tests/*.t

pub:
  rm dist -r
  poetry publish --build
