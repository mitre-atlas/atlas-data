from argparse import ArgumentParser
from datetime import datetime
import json
from pathlib import Path

from schema import Optional, Schema

# Local directory
from schemas.atlas_matrix import atlas_output_schema
from schemas.atlas_obj import case_study_schema

"""
Generates JSON Schema Draft-07 files describing ATLAS.yaml and case study files
from the ATLAS website.

Reads from the schemas directory in this repository.

Run this script with `python -m tools.generate_schema` to allow for local imports.
"""

def set_optional_keys(schema_obj, keys):
    """Sets the specified keys on the Schema object to Optional."""
    for key in keys:
        # Set the key to be optional
        schema_obj._schema[Optional(key)] = schema_obj._schema[key]
        # Remove existing required key
        del schema_obj._schema[key]

 
def update_json_file(output_filepath, new_json, data_name):
    # Take current (old) contents of file and replace the date with the current date
    old_contents = {}
    try:
        with open(output_filepath, 'r') as f:
            old_contents = json.load(f)
            old_contents['description'] = f'Generated on {datetime.now().strftime("%Y-%m-%d")}'
            # The atlas_website_case_study_schema doesn't have these keys
            # if this fails, it goes to the except, then keeps going without issue
            old_contents['matrices']['items']['description'] = f'Generated on {datetime.now().strftime("%Y-%m-%d")}'
    except:
        pass

    # If old and new contents (with the replaced date) have different contents, significant changes have been made so update the file
    if not (old_contents == new_json):
        with open(output_filepath, 'w') as f:
            json.dump(new_json, f, indent=4)
            print(f'Wrote {data_name} to {output_filepath}')
    else:
        print(f'No changes to {data_name}')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--output", "-o", type=str, default="dist/schemas", help="Output directory")
    args = parser.parse_args()

    # Create output directories as needed
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Overall ATLAS YAML
    atlas_json_schema = atlas_output_schema.json_schema('atlas_output_schema')
    output_filepath = output_dir / 'atlas_output_schema.json'
    update_json_file(output_filepath, atlas_json_schema, 'ATLAS.yaml schema')

    # ATLAS website case study

    # Set the `id` and `object-type `fields as optional
    # Case study builder files may not yet have them, but downloaded existing case studies do
    set_optional_keys(case_study_schema, ['id', 'object-type'])

    # Generate JSON schema from pre-defined schema

    # The website's version of a case study file includes the case study object under the key `study`
    # as well as an optional `meta` key containing date created, etc., populated upon website
    # case study builder download
    name = 'ATLAS Website Case Study Schema'
    description = f'Generated on {datetime.now().strftime("%Y-%m-%d")}'
    standalone_case_study_schema = Schema(
        {
            "study": case_study_schema.schema,
            Optional("meta"): {
                # Handle any keys and values
                str: object
            }
        },
        ignore_extra_keys=True,
        name=name,
        description=description)

    # Convert to JSON Schema
    atlas_case_study_json_schema = standalone_case_study_schema.json_schema('atlas_website_case_study_schema')

    # Manipulate JSON to ensure incident date is a date of format YYYY-MM-DD
    # Currently schema library does not output a string format
    # https://json-schema.org/understanding-json-schema/reference/string.html#dates-and-times
    atlas_case_study_json_schema['properties']['study']['properties']['incident-date'] = {
        "anyOf": [
            {
                # Preferred format
                "type": "string",
                "format": "date"
            },
            {
                # Continue accepting old format, which will be converted to preferred upon re-download
                "type": "string",
                "format": "date-time"
            }
        ]
    }

    # Output schema to file
    output_filepath = output_dir / 'atlas_website_case_study_schema.json'
    update_json_file(output_filepath, atlas_case_study_json_schema, 'ATLAS case study schema')
