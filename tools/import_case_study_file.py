from argparse import ArgumentParser
from functools import partial
from pathlib import Path
import re

import yaml

from create_matrix import load_atlas_yaml

"""
Imports case study files into ATLAS data as newly-IDed files.

Case study files are those that have been downloaded from the ATLAS website's /studies/create page.

ATLAS IDs are converted to expressions that use ATLAS YAML anchors.
"""

# Numeric portion of an ATLAS case study ID
REGEX_CS_ID_NUM = re.compile(r'AML\.CS(\d+)')
# Match for any ATLAS tactic, technique, or subtechnique ID
REGEX_ID = re.compile(r'AML\.TA?(?:\d+)(?:\.\d+)?')
# Markdown link to a tactics or techniques page - captures title and ID part of URL
REGEX_INTERNAL_LINK = re.compile(r'\[([^\[]+)\]\(\/(?:techniques|tactics)\/(.*?)\)')
# Captures string version of 'incident-date: YYYY-MM-DD', trimming off end of fully-formatted ISO
# ex.  !!timestamp "2021-11-01T00:00:00.000Z", !!timestamp "2022-02-15 02:40:33+00:00"
REGEX_INCIDENT_DATE = re.compile(r'!!timestamp "(\d{4}-\d{2}-\d{2})(?:[\d:\.+TZ ]+)?"')

def main():
    parser = ArgumentParser('Imports case study files into ATLAS data as newly-IDed files.')
    parser.add_argument("files", type=str, nargs="+", help="Path to case study file(s)")
    args = parser.parse_args()

    # Construct dictionary of ATLAS IDs to anchor variable names
    _, anchor2obj = load_atlas_yaml('data/matrix.yaml')
    id2anchor = {obj['id']: anchor for (anchor, obj) in anchor2obj.items()}

    # Use ID-to-anchor dictionary in regex sub handlers
    replace_link_anchor = partial(replace_link, id2anchor)
    replace_id_anchor = partial(replace_id, id2anchor)

    # Parse and output case study files
    for file in args.files:

        # Find next ATLAS ID and path to that new YAML file in data/case-studies/
        new_filepath = find_next_filepath()
        new_id = new_filepath.stem

        # read_case_study_file(file, sub_id_anchor, new_filepath)

        with open(file, 'r') as f:
            # Read in file
            data = yaml.safe_load(f)
            # Case study file data is held in 'study' key
            case_study = data['study']

            # Convert to string representation for regex
            data_str = yaml.dump(case_study, default_flow_style=False, sort_keys=False, default_style='"')

            # Replace link anchors with template expressions
            data_str = REGEX_INTERNAL_LINK.sub(replace_link_anchor, data_str)
            # Replace IDs with template expressions
            data_str = REGEX_ID.sub(replace_id_anchor, data_str)
            # Trim incident dates, which may be in full ISO8601 format
            data_str = REGEX_INCIDENT_DATE.sub(replace_timestamp, data_str)

            # Load back in from string representation
            case_study = yaml.safe_load(data_str)

            # Strip newlines on summary
            case_study['summary'] = case_study['summary'].strip()
            # Strip newlines on procedure descriptions
            for step in case_study['procedure']:
                step['description'] = step['description'].strip()

            # Add new ID and case study object type at beginning of dict
            new_case_study = {
                'id': new_id,
                'object-type': 'case-study'
            }
            new_case_study.update(case_study)

            # Write out new individual case study file
            with open(new_filepath, 'w') as o:
                yaml.dump(new_case_study, o, default_flow_style=False, explicit_start=True, sort_keys=False)

            print(f'{new_filepath} <- {file}')

        print(f'\nImported {len(args.files)} file(s) - review, run pytest for spellcheck exclusions, then run tools/create_matrix.py for ATLAS.yaml.')

def find_next_filepath():
    """Returns a Path to a case study YAML file with next available ATLAS ID."""
    # Open output directory, assumed to be from root project dir
    case_study_dir = Path('data/case-studies')
    # Retrieve all YAML files and get the last file in alphabetical order
    filepaths = sorted(case_study_dir.glob('*.yaml'))
    # Filepath with highest ID number
    latest_filepath = filepaths[-1]

    # Parse out the numeric portion of the case study ID filename
    match = REGEX_CS_ID_NUM.match(latest_filepath.stem)

    if match:
        # Only 1 match expected, i.e. 0015
        cur_id_num_str = match.groups()[0]
        # Get next integer, i.e. 16
        next_id_num = int(cur_id_num_str) + 1
        # Padded by zeros, i.e. 0016
        next_id_num_str = '{:04d}'.format(next_id_num)
        # Replace current number with the next increment
        next_filepath_str = latest_filepath.as_posix().replace(cur_id_num_str, next_id_num_str)
        # Return as a Path
        return Path(next_filepath_str)

    # Otherwise no case study ID match
    return None

def replace_timestamp(match):
    """Returns a string representation of a YAML timestamp with only the YYYY-MM-DD date portion."""
    if match:
        date = match.group(1)

        return f'!!timestamp "{date}"'

    return match.group()

def replace_id(id2anchor, match):
    """Returns a string Jinja expression that accesses the id key of the anchor.

    Ex. {{anchor.id}}
    """
    if match:
        atlas_id = match.group()
        return '{{' + id2anchor[atlas_id] + '.id}}'

    return match.group()

def replace_link(id2anchor, match):
    """Returns a string Jinja expression that creates an internal Markdown link for tactics and techniques.

    Ex. [{{anchor.name}}](/techniques/{{anchor.id}})
    """
    if match:
        # Unwrap matches
        full_link = match.group(0)
        title = match.group(1)
        atlas_id = match.group(2)
        # Get anchor variable name
        anchor = id2anchor[atlas_id]

        # Replace values with template expressions {{ anchor.xyz }}
        # Note that double brackets evaluate to one bracket
        full_link = full_link.replace(title, f'{{{{{anchor}.name}}}}')
        full_link = full_link.replace(atlas_id, f'{{{{{anchor}.id}}}}')

        return full_link

    return m.group(0)

if __name__ == '__main__':
    main()