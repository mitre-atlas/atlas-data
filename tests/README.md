# Tests

This test suite uses `pytest` to validate ATLAS data in `ATLAS.yaml`, as constructed from `data/matrix.yaml` via `tools/create_matrix.py`.

Current tests include schema validation, Markdown link syntax, and warnings for spelling.  To add words to the spellcheck,
edit `spellcheck.py` in this directory.

## Run

Install dependencies using `pip install -r tests/requirements.txt`, then run the test suite from the root of this project using `pytest`.
