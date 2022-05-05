# Data

ATLAS data is stored in YAML files designed to be easy to read and edit, as well as to load, parse, and validate.

`data.yaml` is the entry point, describing the ID, which will become the name of the output YAML file, as well as listing relative paths to matrix directories.

## Matrices

A matrix directory contains the following files:

- `matrix.yaml` contains metadata, tactics in matrix order, and includes the other data files.

- `tactics.yaml` contains ATLAS tactics, which represent adversary goals.

- `techniques.yaml` contains ATLAS techniques and subtechniques, which represent the means by which adversaries achieve tactical goals.

- `case-studies/` is a directory containing ATLAS case study files, which describe select machine learning attack incidents and how they map to the ATLAS framework.

## Anchors and templates

Each tactic and technique object has a YAML anchor, which is prefaced with `&`.

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

Modify `tactics.yaml` and `techniques.yaml` for changes to the ATLAS framework itself.

Ensure that object IDs are unique and follow the patterns defined in the schema.  See definitions in `schemas` for ID patterns and object schemas.

### Case studies

Case study files, such as those downloaded from the ATLAS website, can be added manually or via the `tools/import_case_study_file.py` script.

To import one or more case study files , run this from the project root:
```
python tools/import_case_study_file.py <path to file 1> <path to file 2>
```

Each imported file has hardcoded tactic and technique IDs replaced with anchors, is assigned a case study ID, and is output `data/case-studies/<ID>.yaml`.

### Custom data

Custom ATLAS objects can also be added as new YAML files in `data/matrix.yaml`:

```yaml
data:
  - !include tactics.yaml         # Path to YAML file containing ATLAS objects
  - !include techniques.yaml      # Relative to this data directory
  - !include case-studies/*.yaml  # Wildcard syntax is supported
  - !include custom-objs.yaml     # Add other custom files
```

Objects added via the `!include` syntax can be found in re-generated `ATLAS.yaml` in the corresponding `tactics`/`techniques`/`case-studies` depending on the object's `object-type`.

### Output generation

To re-generate `dist/ATLAS.yaml` after modifying these source files, run this from the project root:
```
python tools/create_matrix.py
```

Use the argument `-o <other_directory>` to output `ATLAS.yaml` into another directory.