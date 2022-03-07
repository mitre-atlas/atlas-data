# MITRE | ATLAS Data

ATLAS enables researchers to navigate the landscape of threats to artificial intelligence and machine learning systems.  Visit https://atlas.mitre.org for more information.

This repository contains the tactics, techniques, and case studies data used to populate the ATLAS website and associated tools.

ATLAS data is stored in YAML files designed to be easy to read and edit, as well as to load, parse, and validate.

## Distributed files

Located the `dist` directory:

- `ATLAS.yaml`
    + All ATLAS-related data available in one file
    + Top-level keys
        ```yaml
        id: ATLAS
        name: ATLAS Machine Learning Threat Matrix
        version: Version number for this data release
        tactics: List of tactics objects
        techniques: List of technique and subtechnique objects
        case-studies: List of case study objects
        ```

### Usage

The following code blocks show examples of parsing ATLAS data in Python and NodeJS.  Assume `atlas_data_filepath` holds the path to the ATLAS.yaml file.

```python
# pip install pyyaml
import yaml

with open(atlas_data_filepath) as f:
    # Dictionary containing the above keys
    data = yaml.safe_load(f)
    tactics = data['tactics']
    techniques = data['techniques']
    studies = data['case-studies']
```

```js
const fs = require('fs')
const yaml = require('js-yaml') // npm install js-yaml

// Retrieve the threat matrix YAML data and populate store upon start
fs.readFile(atlas_data_filepath, 'utf-8', (err, contents) => {
    if (err) {
        console.error(err)
        return
    }

    // Parse YAML
    const data = yaml.load(contents)
    const tactics = data['tactics']
    const techniques = data['techniques']
    const studies = data['case-studies']
})
```

## Development

Scripts in the `tools` directory update the files above.

### Installation

Install dependencies via `pip install -r tools/requirements.txt`

### Usage

To update the ATLAS.yaml data file, run
```
python tools/create_matrix.py
```

When tactics and techniques update in `atlas-data`, run
```
python tools/generate_stix.py
python tools/generate_navigator_layer.py --layer matrix
```
Omit the `--layer` option above to generate all outputs.

Run each script with `-h` for further options.

## Related work

ATLAS is modeled after the [MITRE ATT&CK:registered: framework](https://attack.mitre.org).

[ATLAS data in STIX and ATT&CK Navigator layer formats](https://github.mitre.org/mitre-atlas/atlas-navigator-data) for use with the [ATLAS Navigator](https://mitre-atlas.github.io/attack-navigator/)
