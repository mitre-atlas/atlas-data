# Data Tools

Scripts for generating ATLAS data.
- `get_attack.py` downloads ATT&CK Enterprise data and saves it as YAML
- `create_matrix.py` generates tactics and techniques YAML files filled in with ATT&CK data.
- `generate_stix.py` adds ATLAS as a platform on top of ATT&CK and outputs a STIX JSON file.
- `generate_navigator_layer.py` creates ATT&CK Navigator-compatible layer files highlighting the ATLAS matrix, case study frequencies, and each case study's techniques.

## Setup

1. Use Python 3.6+.

2. Set up a virtual environment and install dependencies.
```
pip -m venv venv
pip install --upgrade pip
pip install -r tools/requirements.txt
```

3. Obtain a local copy of ATT&CK Enterprise data by running `python tools/get_attack.py`, which outputs the file `data/enterprise-attack-{version}.yaml`.

## Run

To validate the ATLAS YAML data, run ```python tools/data_validation.py```.

To create the full ATLAS YAML file, run ```python tools/create_matrix.py```.

To create the ATLAS + ATTACK STIX JSON file, run ```python tools/generate_stix.py```.

To create ATLAS Navigator layer files, including the ATLAS Matrix, case study frequency, and individual case study layers, run ```python tools/generate_navigator_layer.py```.

Run each script with `-h` to see full options.
