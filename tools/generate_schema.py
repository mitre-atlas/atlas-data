from argparse import ArgumentParser
from datetime import datetime
import json
from pathlib import Path

from schema import Optional, Schema

# Local directory
from schemas.atlas_matrix import atlas_output_schema
from schemas.atlas_obj import case_study_schema, CASE_STUDY_VERSION

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

def has_json_schema_changed(output_filepath, new_json):
    """Returns True if the contents of the existing JSON schema file differ from the current schema."""

    # Save off and remove the description key (Generated on YYYY-MM-DD)
    # to enable comparison of other fields
    description_key = 'description'
    new_json_description = new_json[description_key]
    del new_json[description_key]

    with open(output_filepath, 'r') as f:
        # Load the existing JSON schema and remove its description
        existing_json = json.load(f)
        del existing_json[description_key]

        # Compare the JSON objects, without description
        are_json_schemas_equal = existing_json == new_json

        # Put back new JSON schema description
        new_json[description_key] = new_json_description

        # Returns True if the json schemas have changed
        return not are_json_schemas_equal


def update_json_file(output_filepath, new_json, data_name):
    # If old and new contents (with the replaced date) have different contents, significant changes have been made so update the file
    if has_json_schema_changed(output_filepath, new_json):
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

    # Output overall ATLAS YAML
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
    # Description is not specified in the Python schema, but here to avoid generating in the overall JSON schema
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
    atlas_case_study_json_schema['properties']['study']['properties']['incident-date']['format'] = 'date'
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

    # Mark deprecated fields with a message
    with open('schemas/case_study_deprecated_fields.json', 'r') as f:
        deprecated = json.load(f)
        for dep in deprecated:
            atlas_case_study_json_schema['properties']['study']['properties'][dep['field']] = {
                'deprecated': 'true',
                'depMessage': '`' + dep['field'] + '`' + ' deprecated as of version '+ dep['version']
            }
            if 'replaced-by' in dep:
                atlas_case_study_json_schema['properties']['study']['properties'][dep['field']]['depMessage'] += '; replaced by ' + '`'+ dep['replaced-by'] + '`'
            else:
                atlas_case_study_json_schema['properties']['study']['properties'][dep['field']]['depMessage'] += '; field removed'

    atlas_case_study_json_schema['$version'] = CASE_STUDY_VERSION

    # Output schema to file
    output_filepath = output_dir / 'atlas_website_case_study_schema.json'
    update_json_file(output_filepath, atlas_case_study_json_schema, 'ATLAS website case study schema')
