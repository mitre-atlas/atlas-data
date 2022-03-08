# Tools

Scripts to generate the distributed files and import data files.

- `create_matrix.py` compiles the threat matrix data sources into a single standard YAML file, `ATLAS.yaml`. See more about [generating outputs from data](../data/README.md#output-generation)

- `generate_schema.py` outputs JSON Schema files for external validation of `ATLAS.yaml` and case study files. See more on [schema files](../schemas/README.md).

- `import_case_study_file.py` imports case study files from the ATLAS website into ATLAS data as newly-IDed, templated files.  See more about [updating case studies](../data/README.md#case-studies).

Run each script with `-h` to see full options.

## Development Setup

1. Use Python 3.6+.

2. Set up a [virtual environment](https://docs.python.org/3/library/venv.html). For example:
    ```
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    ```


3. Install dependencies for running tools scripts and tests.
    ```
    pip install -r tools/requirements.txt
    pip install -r tests/requirements.txt
    ```