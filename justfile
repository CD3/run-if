set positional-arguments
test *args:
        poetry run pytest -s "$@"
