# Data

ATLAS data is stored in YAML files designed to be easy to read and edit, as well as to load, parse, and validate.

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
This data may be introduced to a victim system via [ML Supply Chain Compromise](https://atlas.mitre.org/techniques/AML.T0010)
```

## Updating the data

### ATLAS data

Modify `tactics.yaml` and `techniques.yaml` for changes to the ATLAS framework itself.

New case studies can be added via the `tools/import_case_study_file.py` script.  See `tools/README.md` for more details.

Ensure that object IDs are unique and follow the patterns defined in the schema.  See definitions in `dist/schemas/atlas_matrix_schema.json` for ID patterns and object schemas.

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

### Generate output

Re-generate ATLAS.yaml after modifying these source files, run
```
python tools/create_matrix.py
```
