# advmlthreatmatrix data

Data for the Adversarial Machine Learning Threat Matrix.

The advmlthreatmatrix data is stored in YAML files designed to be easy to read and edit, but also easy to load, parse, and validate.

`matrix.yaml` contains the metadata for the matrix and references the underlying data files for tactics and techniques. It also allows for referencing external threat intelligence such as ATT&CK.

`tactics.yaml` contains all of the adversarial ML tactics.

`techniques.yaml` contains all of the adversarial ML techniques.

`case-studies.yaml` contains all of the adversarial ML case studies.

`schema.yaml` defines the schema for the matrix, tactic, technique, and case-study objects.

### tools

`tools/get_attack.py` is a simple script for downloading ATT&CK STIX data and converting it into a YAML format compatible with the advmlthreatmatrix data.

`tools/create_matrix.py` compiles the threat matrix data sources into a single standard YAML file.

`tools/data_validation.py` validates the YAML files for schema and link syntax, outputting any errors to console or to file via the `-f` option.

### non-standard YAML

The advmlthreatmatrix data files contain several non-standard YAML features.
The files use cross-document anchors for referencing objects, an !include constructor for loading multiple data sources, and some custom parsing for referencing objects in text blocks.
Parsing these non-standard features is handled by `tools/create_matrix.py` which outputs a standard YAML file.
