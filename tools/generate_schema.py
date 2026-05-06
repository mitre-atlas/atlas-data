from argparse import ArgumentParser
from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path

# Local directory
from schemas.atlas_matrix import atlas_output_schema
from schemas.atlas_obj import (
    CASE_STUDY_VERSION,
)
from schemas.website_submission import (
    contributions_schema,
    website_case_study_wrapper_schema,
    WEBSITE_SUBMISSION_VERSION
)

"""
Generates JSON Schema Draft-07 files describing ATLAS.yaml and website-generated
submission files.

Reads from the schemas directory in this repository.

Run this script with `python -m tools.generate_schema` to allow for local imports.
"""

def has_json_schema_changed(output_filepath, new_json):
    """Returns True if the contents of the existing JSON schema file differ from the current schema."""

    # Should be considered changed if it doesn't exist
    if not Path(output_filepath).exists():
        return True

    # Save off and remove the description key (Generated on YYYY-MM-DD)
    # to enable comparison of other fields
    description_key = 'description'
    new_json_description = new_json.pop(description_key, None)

    with open(output_filepath, 'r') as f:
        # Load the existing JSON schema and remove its description
        existing_json = json.load(f)
        existing_json.pop(description_key, None)

        # Compare the JSON objects, without description
        are_json_schemas_equal = existing_json == new_json

        # Put back new JSON schema description
        if new_json_description is not None:
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
    atlas_case_study_json_schema = website_case_study_wrapper_schema.json_schema('atlas_website_case_study_schema')
    atlas_case_study_json_schema['title'] = 'ATLAS Website Case Study Schema'
    atlas_case_study_json_schema['description'] = f'Generated on {datetime.now().strftime("%Y-%m-%d")}'

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

    # Contributions unified schema
    description = f'Generated on {datetime.now().strftime("%Y-%m-%d")}'

    # Generate parent contributions JSON Schema via Python-level composition
    atlas_contribution_json_schema = contributions_schema.json_schema('atlas_contribution_schema')
    atlas_contribution_json_schema['$id'] = 'atlas_contribution_schema'
    atlas_contribution_json_schema['description'] = description
    atlas_contribution_json_schema['$version'] = WEBSITE_SUBMISSION_VERSION

    # Reuse the cleaned website case study wrapper in the contributions schema.
    patched_case = {
        key: deepcopy(value)
        for key, value in atlas_case_study_json_schema.items()
        if key not in {'$id', '$schema', 'title', 'definitions', '$version', 'description'}
    }
    patched_case['properties']['study']['if'] = {
        'properties': {
            'case-study-type': {
                'const': 'incident',
            },
        },
        'required': ['case-study-type'],
    }
    patched_case['properties']['study']['then'] = {
        'required': ['reporter'],
    }
    _defs_key = 'definitions' if 'definitions' in atlas_contribution_json_schema else '$defs'
    atlas_contribution_json_schema[_defs_key]['case_study'] = patched_case

    # Output contributions schema to file
    output_filepath = output_dir / "atlas_contribution_schema.json"
    update_json_file(output_filepath, atlas_contribution_json_schema, "ATLAS contribution schema")
