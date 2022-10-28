# Data

ATLAS data is stored in YAML files designed to be easy to read and edit, as well as to load, parse, and validate.  Each file contains a standard YAML 1.1 document.

## Files

`data.yaml` is the entry point for data definition.  It describes the ID, which will become the name of the output YAML file, as well as listing relative paths to matrix directories and other top-level data.


For example, the ATLAS `data.yaml` is as follows:
```yaml
---

id: ATLAS
name: Adversarial Threat Landscape for AI Systems
version: 4.1.0

matrices:
  - !include .

data:
  - !include case-studies/*.yaml
```

## Matrices

A matrix directory contains a `matrix.yaml` and data object files.

Files in the ATLAS matrix directory:
- `matrix.yaml` contains metadata, tactics in matrix order, and relative filepaths to the other data files below.
- `tactics.yaml` contains ATLAS tactics, which represent adversary goals.
- `techniques.yaml` contains ATLAS techniques and subtechniques, which represent the means by which adversaries achieve tactical goals.

## Other top-level data
Top-level data can reference data objects across matrices.

- `case-studies/` is a directory containing ATLAS case study files, which describe select machine learning attack incidents and how they map to the ATLAS framework.

## Anchors and templates

Each referenceable data object has a YAML anchor, which is prefaced with `&`.  For example, a technique object defined in `techniques.yaml`:

```yaml
- &supply_chain
  id: AML.T0010
  name: ML Supply Chain Compromise
  object-type: technique
```

Anchors are used as variable names throughout the files in template expressions, wrapped with `{{ }}`.

```jinja
This data may be introduced to a victim system via [{{supply_chain.name}}](/techniques/{{supply_chain.id}}).
```

When using `tools/create_matrix.py` to generate the fully-populated `ATLAS.yaml` data file, these source files are evaluated as templates.  The output of the evaluating the example above:

```md
This data may be introduced to a victim system via [ML Supply Chain Compromise](/techniques/AML.T0010)
```

## Updating the data

### Tactics and techniques

Modify `tactics.yaml` and `techniques.yaml` for changes to the main ATLAS matrix.

Ensure that object IDs are unique and follow the patterns defined in the schema.  See definitions in `schemas` for ID patterns and object schemas.

### Case studies

Case study files, such as those downloaded from the ATLAS website, can be added via the `tools/import_case_study_file.py` script.

To import one or more case study files , run this from the project root:
```
python -m tools.import_case_study_file <path to file 1> <path to file 2>
```

Each imported file has hardcoded tactic and technique IDs replaced with anchors, is assigned a case study ID, and is output `data/case-studies/<ID>.yaml`.

### Custom data

Custom data objects can also be added to matrices as new YAML files in `matrix.yaml` files:

```yaml
data:
  - !include tactics.yaml         # Path to YAML file containing ATLAS objects
  - !include techniques.yaml      # Relative to this data directory
  - !include case-studies/*.yaml  # Wildcard syntax is supported
  - !include custom-objs.yaml     # Add other custom files
```

####  Referencing other YAML files

The `!include` directive accepts relative filepaths to either:
  1. A named YAML file containing a list of data objects, or
  2. A directory containing YAML files with a single data object in each file, specified using the wildcard syntax above

Objects added via the `!include` syntax can be found in re-generated `ATLAS.yaml` under `matrices`, with a key that is a plural version of the object's `object-type` field.

### Additional matrices

To add a new matrix, create a new directory inside `data` containing a `matrix.yaml`.

In this example, we've created a new directory called `my-matrix` with the `matrix.yaml` below  This new matrix has its own tactics and techniques files.

  ```yaml
  ---

  id: custom-matrix
  name: Custom Matrix

  tactics:
  - "{{hello.id}}"

  data:
  - !include my-tactics.yaml
  - !include my-techniques.yaml
  ```

Lastly, update `data.yaml` to include the relative path to the new matrix directory.

  ```yaml
  matrices:
    - !include .
    - !include my-matrix
  ```

### Output generation

To re-generate `dist/ATLAS.yaml` after modifying these source files, run this from the project root:
```
python tools/create_matrix.py
```

Use the argument `-o <other_directory>` to output `ATLAS.yaml` into another directory.