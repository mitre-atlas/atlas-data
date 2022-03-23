# MITRE | ATLAS Data

ATLAS enables researchers to navigate the landscape of threats to artificial intelligence and machine learning systems.  Visit https://atlas.mitre.org for more information.

This repository contains the tactics, techniques, and case studies data used by the ATLAS website and associated tools.

## Distributed files

Located the `dist` directory:

- `ATLAS.yaml`
    + All ATLAS-related data available in one file
    + See the schemas and usage below for more details. Top-level keys include:
        ```yaml
        id: ATLAS
        name: ATLAS Machine Learning Threat Matrix
        version: Version number for this data release
        tactics: List of tactics objects
        techniques: List of technique and subtechnique objects
        case-studies: List of case study objects
        ```
- `schemas/`
    + Optional JSON Schema files for validation use
    + `atlas_matrix_schema.json`
        * Describes the `ATLAS.yaml` format
    + `atlas_website_case_study_schema.json`
        * Describes the case study file format

### Example usage

The following code blocks show examples of parsing ATLAS data.  Assume `atlas_data_filepath` holds the path to the `ATLAS.yaml` file.

#### Python
```python
# pip install pyyaml
import yaml

with open(atlas_data_filepath) as f:
    # Parse YAML
    data = yaml.safe_load(f)

    tactics = data['tactics']
    techniques = data['techniques']
    studies = data['case-studies']
```

#### NodeJS
```js
const fs = require('fs')
// npm install js-yaml
const yaml = require('js-yaml')

fs.readFile(atlas_data_filepath, 'utf-8', (_, contents) => {
    // Parse YAML
    const data = yaml.load(contents)

    const tactics = data['tactics']
    const techniques = data['techniques']
    const studies = data['case-studies']
})
```

### JSON Schema validation example

JSON Schema files are generated from this project's internal [schemas](schemas/README.md) for other tools to use. For example, the ATLAS website validates uploaded case study files against the case study schema file with the following:

#### NodeJS

```js
// npm install jsonschema
import { validate } from 'jsonschema'
import caseStudySchema from '<path_to_case_study_schema_file>'

// Assume this is a populated website case study object
const caseStudyObj = {...}

// Validate case study object against schema and emit errors that may occur from nested `anyOf` validations
const validatorResult = validate(caseStudyObj, caseStudySchema, { nestedErrors: true })

if (validatorResult.valid) {
    // Good
} else {
    // Process validatorResult.errors
}

```

## Development

This repository also contains the source data and scripts to customize and expand the ATLAS framework.  See [setup instructions](tools/README.md#development-setup) and the READMEs in each directory linked below for usage.

- [Data](data/README.md) holds templated data for ATLAS tactics, techniques, and case studies, from which `ATLAS.yaml` is generated.
- [Schemas](schemas/README.md) defines each ATLAS object type and ID.
- [Tools](tools/README.md) contains scripts to generate the distributed files and import data files.

**Testing**
This project uses `pytest` for data validation. See [tests](tests/README.md) for more information.


## Related work

ATLAS is modeled after the [MITRE ATT&CK® framework](https://attack.mitre.org). ATLAS tactics and techniques can be complementary to those in ATT&CK.

ATLAS data is also available in [STIX and ATT&CK Navigator layer formats](https://github.mitre.org/mitre-atlas/atlas-navigator-data) for use with the [ATLAS Navigator](https://mitre-atlas.github.io/attack-navigator/).
