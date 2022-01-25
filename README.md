# MITRE | ATLAS Data

The ATLAS data is stored in YAML files designed to be easy to read and edit, as well as to load, parse, and validate.

`ATLAS.yaml`

## Source data

`matrix.yaml` contains the metadata for the matrix and references the underlying data files for tactics and techniques.
It also allows for referencing external threat intelligence such as ATT&CK.

`tactics.yaml` contains all of the adversarial ML tactics.

`techniques.yaml` contains all of the adversarial ML techniques.

`case-studies.yaml` contains all of the adversarial ML case studies.

`schema.yaml` defines the schema for the matrix, tactic, technique, and case-study objects.

### Tools

`tools/create_matrix.py` compiles the threat matrix data sources into a single standard YAML file.

`tools/data_validation.py` validates the YAML files for schema and link syntax, outputting any errors to console or to file via the `-f` option.

`tools/generate_stix` creates the ATLAS + ATTACK STIX JSON file.

`tools/generate_navigator_layer` creates ATLAS Navigator layer files, including the ATLAS Matrix, case study frequency, and individual case study layers.

Run each script with `-h` to see full options.

#### Development Setup

1. Use Python 3.6+.

2. Set up a [virtual environment[(https://docs.python.org/3/library/venv.html)] and install dependencies.
```
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

3. (Optional) To be able to run tests, `pip install -r tests/requirements.txt`

### A Note on Non-Standard YAML

The ATLAS data files contain several non-standard YAML features.
The files use cross-document anchors for referencing objects, an !include constructor for loading multiple data sources, and some custom parsing for referencing objects in text blocks.
Parsing these non-standard features is handled by `tools/create_matrix.py`.
