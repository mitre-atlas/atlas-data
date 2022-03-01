# Tools

The ATLAS data is stored in YAML files designed to be easy to read and edit, as well as to load, parse, and validate.

`create_matrix.py` compiles the threat matrix data sources into a single standard YAML file.

`import_case_study_file.py` imports case study files from the ATLAS website into ATLAS data as newly-IDed files.

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

