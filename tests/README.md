# Tests

This project uses `pytest` to validate ATLAS data in `ATLAS.yaml`, as constructed from `data/matrix.yaml` via `tools/create_matrix.py`.

Test fixtures are defined in `conftest.py` in the project root, for access to tools and schemas.

Current tests include schema validation, Markdown link syntax, and warnings for spelling.  To add words to the spellcheck, edit `custom_words.txt` in this directory.

## Usage

Install dependencies using `pip install -r tests/requirements.txt`, then run the test suite from the root of this project using `pytest`.
