# Distributed files

This directory holds generated data files for direct use.

- `ATLAS.yaml`
    + All ATLAS-related data available in one file
    + See the schemas and usage below for more details. Top-level keys include:
        ```yaml
        id: ATLAS
        name: Adversarial Threat Landscape for AI Systems
        version: Version number for this data release
        matrices: List of matrix data
        - id: ATLAS
          name: ATLAS Machine Learning Threat Matrix
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

    first_matrix = data['matrices'][0]
    tactics = first_matrix['tactics']
    techniques = first_matrix['techniques']

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

    const first_matrix = data['matrices'][0]

    const tactics = first_matrix['tactics']
    const techniques = first_matrix['techniques']

    const studies = data['case-studies']
})
```

### JSON Schema validation example

JSON Schema files are generated from this project's internal [schemas](../schemas/README.md) for other tools to use. For example, the ATLAS website validates uploaded case study files against the case study schema file with the following:

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
