# Schemas

The project uses the [schema library](https://github.com/keleshev/schema) to define and validate its data.

- `atlas_id.py` defines ATLAS ID regular expression patterns.
- `atlas_matrix.py` holds the schema for the `ATLAS.yaml` file.
- `atlas_obj.py` holds schemas for tactic, technique, subtechnique, and case study objects.

## Usage

The schemas in this directory are used as test fixures in `conftest.py`. `tests/schema_validation.py` validates each ATLAS data object.

Additionally, JSON Schema files for `ATLAS.yaml` and case study files are available at `dist/schemas/` for other tools to use.  For example, the ATLAS website validates uploaded case study files against the case study schema file.

### Output generation

To re-generate JSON Schema files after modifying the schemas in this directory, run this from the project root:
```
python -m tools.generate_schema
```
