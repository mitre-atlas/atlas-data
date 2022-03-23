from argparse import ArgumentParser
from datetime import datetime
import json
from pathlib import Path

from schema import Optional, Schema

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

    # ATLAS website case study

    # Set the `id` field as optional as case study files from the ATLAS website may not yet have IDs
    case_study_schema._schema[Optional('id')] = case_study_schema._schema['id']
    del case_study_schema._schema['id']

    # Generate JSON schema from pre-defined schema

    # The website's version of a case study file includes the case study object under the key `study`
    # as well as an optional `meta` key containing date created, etc., populated upon website
    # case study builder download
    name = 'ATLAS Website Case Study Schema'
    description = f'Generated on {datetime.now().strftime("%Y-%m-%d")}'
    standalone_case_study_schema = Schema(
        {
            "study": case_study_schema.schema,
            Optional("meta"): {}
        },
        name=name,
        description=description)

    # Convert to JSON Schema
    atlas_case_study_json_schema = standalone_case_study_schema.json_schema('atlas_website_case_study_schema')

    # Manipulate JSON to ensure incident date is a date of format YYYY-MM-DD
    # Currently schema library does not output a string format
    # https://json-schema.org/understanding-json-schema/reference/string.html#dates-and-times
    atlas_case_study_json_schema['properties']['study']['properties']['incident-date']['format'] = 'date'

    # Output schema to file
    output_filepath = output_dir / 'atlas_website_case_study_schema.json'
    with open(output_filepath, 'w') as f:
        json.dump(atlas_case_study_json_schema, f, indent=4)
        print(f'Wrote ATLAS case study schema to {output_filepath}')
