from argparse import ArgumentParser
from datetime import datetime
import json
from pathlib import Path

from schema import Schema

# Local directory
from schemas.atlas_matrix import atlas_matrix_schema
from schemas.atlas_obj import case_study_schema

"""
Generates JSON Schema Draft-07 files describing ATLAS.yaml and case study files
from the ATLAS website.

Reads from the schemas directory in this repository.

Run this script with `python -m tools.generate_schema` to allow for local imports.
"""

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--output", "-o", type=str, default="dist/schemas", help="Output directory")
    args = parser.parse_args()

    # Create output directories as needed
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Overall ATLAS YAML
    atlas_json_schema = atlas_matrix_schema.json_schema('atlas_matrix_schema')
    output_filepath = output_dir / 'atlas_matrix_schema.json'
    with open(output_filepath, 'w') as f:
        json.dump(atlas_json_schema, f, indent=4)
        print(f'Wrote ATLAS.yaml schema to {output_filepath}')

    # ATLAS case study

    # Generate JSON schema from pre-defined schema, defaulting to no references for a standalone file
    name = 'ATLAS Case Study Schema'
    description = f'Generated on {datetime.now().strftime("%Y-%m-%d")}'
    standalone_case_study_schema = Schema(case_study_schema.schema, name=name, description=description)

    # Remove the `id` required field as case study files from the ATLAS website don't yet have IDs
    del standalone_case_study_schema._schema['id']

    # Convert to JSON Schema
    atlas_case_study_json_schema = standalone_case_study_schema.json_schema('atlas_case_study_schema')

    # Manipulate JSON to ensure incident date is a date of format YYYY-MM-DD
    # Currently schema library does not output a string format
    # https://json-schema.org/understanding-json-schema/reference/string.html#dates-and-times
    atlas_case_study_json_schema['properties']['incident-date']['format'] = 'date'

    # Output schema to file
    output_filepath = output_dir / 'atlas_case_study_schema.json'
    with open(output_filepath, 'w') as f:
        json.dump(atlas_case_study_json_schema, f, indent=4)
        print(f'Wrote ATLAS case study schema to {output_filepath}')
