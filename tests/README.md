# Tests

This test suite uses `pytest` to validate ATLAS data constructed from `data/matrix.yaml` via `tools/create_matrix.py`.

Install dependencies from the `requirements.txt` in this directory, then run the test suite from the root of this project using `pytest`.

Current tests include schema validation, Markdown link syntax, and warnings for spelling.  To add words to the spellcheck,
edit `spellcheck.py` in this directory.
