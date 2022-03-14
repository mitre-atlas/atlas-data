# Tests

This project uses [pytest](https://docs.pytest.org/) to validate ATLAS data.

- `conftest.py`
    + Test fixtures are defined in `conftest.py` in the project root, for access to tools and schemas.
    + Loads ATLAS data as constructed from `data/matrix.yaml` via `tools/create_matrix.py`.
- `tests/test_*.py`
    + Current tests include schema validation, Markdown link syntax, and warnings for spelling.
    + To add words to the spellcheck, edit `custom_words.txt` in this directory.
- `tests/.yamllint` holds custom [YAML lint configuration](https://yamllint.readthedocs.io/en/stable/index.html) rules.

## Installation

Install dependencies using: 
`pip install -r tests/requirements.txt`
`pip install -r tools/requirements.txt`

## Usage

From the root of this project, run `pytest`.

Additional YAML linting can be performed with `yamllint -c tests/.yamllint .`