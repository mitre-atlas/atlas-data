from copy import deepcopy
from argparse import ArgumentParser
import json
from pathlib import Path
import re

import yaml

from create_matrix import load_atlas_data


"""Converts ATLAS YAML data to ATT&CK Navigator layers."""


def generate_individual_case_study_layers(matrix, output_dir,
    individual_case_study_layer_directory='case-study-layers'):
    """
    Outputs a layer JSON file highlighting each individual case study
    and the corresponding techniques used in each one
    """

    domain = 'atlas-v2-+-enterprise-v9-atlas'

    # Base for all layers
    layer_data = {
        "versions": {
            "layer": "4.2",
            "navigator": "4.2"
        },
        "domain": domain
    }

    case_studies = matrix['case-studies']

    # Iterates through each case-study in the matrix file
    for case_study in case_studies:
        # Title at the top of the Navigator tab
        name = case_study['name']
        case_study_id = case_study['id']
        # Appears in layer dropdown
        summary = case_study['summary']
        color = '#C8E6C9'

        # Maps tactic IDs to their name
        tactic_map = []
        for tactic in matrix['tactics']:
            tactic_map.append({
                'id': tactic['id'],
                'name': tactic['name']
            })

        ts = []
        # Build dictionary of techniques used in each specific case study
        # These can be a mix of ATLAS and ATT&CK techniques
        for t in case_study["procedure"]:
            id = t['technique']

            # changes tactic IDs to their navigator compatible names
            for map in tactic_map:
                if t['tactic'] == map['id']:
                        tactic = map['name'].replace(' ','-').lower()

            # separates between parent and sub techniques
            if len(id.split('.')) >= 3 and id.startswith('AML'):
                short_id = id.split('.')[0] + '.' + id.split('.')[1]
                t = {
                    "techniqueID": short_id,
                    "showSubtechniques": True,
                    "tactic": tactic,
                }
                for tss in case_study['procedure']:
                    if short_id == tss['technique'] and short_id not in ts:
                        t = {
                            "techniqueID": short_id,
                            "color": color,
                            "showSubtechniques": True,
                            "tactic": tactic,
                        }

                if t not in ts:
                    ts.append(t)

            elif len(id.split('.')) == 2 and id.startswith('T'):
                t = {
                    "techniqueID": id.split('.')[0],
                    "showSubtechniques": True,
                    "tactic": tactic,
                }
                if t not in ts:
                    ts.append(t)

            t = {
                "techniqueID": id,
                "color": color,
                "tactic": tactic,
            }

            if t not in ts:
                ts.append(t)


        # Construct layer data
        individual_case_study_layer_data = {
            "name": name,
            "description": summary,
            "techniques": ts,
            "legendItems": [
                {
                    "label": "ATLAS technique",
                    "color": color
                }
            ],
        }

        individual_case_study_layer_data = { **layer_data, ** individual_case_study_layer_data}

        # Define output filename
        dir_path = output_dir / individual_case_study_layer_directory
        filename = '{}-case_study_layer.json'.format(case_study_id)
        # Write JSON to file
        write_to_json_file(individual_case_study_layer_data, dir_path, filename)

def generate_case_study_layers(matrix, output_dir, layer_output_directory='default-navigator-layers'):
    """
    Outputs a layer JSON file highlighting the frequency of techniques
    used in all of the case-studies from the matrix
    """

    domain = 'atlas-v2-+-enterprise-v9-atlas'
    # Base for all layers
    layer_data = {
        "versions": {
            "layer": "4.2",
            "navigator": "4.2"
        },
        "domain": domain,
    }

    # Title at the top of the Navigator tab
    name = 'ATLAS Case Study Frequency'
    # Appears in layer dropdown
    description = 'Heatmap of techniques used in ATLAS case studies'

    tactic_map = []
    # creates objects for id's and corresponding tactics
    base_ids = []
    for c in matrix['case-studies']:
        for p in c["procedure"]:
            short_id = deepcopy(p["technique"])
            base_ids.append({
                'id': short_id,
                'tactic': p['tactic'],
                'count': 0
            })

    # finds the frequency of each id and it's corresponding tactic
    case_study_frequency = []
    for group1 in base_ids:
        for group2 in base_ids:
            if group1['id'] == group2['id'] and group1['tactic'] == group2['tactic']:
                group1['count'] = group1['count']+1
        case_study_frequency.append(group1)

    # Build list of ATLAS technique short IDs and associated info
    ts = []
    for tactic in matrix['tactics']:
        tactic_map.append({'id': tactic['id'],'name': tactic['name']})

   # swaps out tactic id for words from the navigator
    for t in base_ids:
        for map in tactic_map:
            if t['tactic'] == map['id']:
                navigator_tactic = map['name'].replace(' ','-').lower()
                t['tactic'] = navigator_tactic

    # creates the list of techniques with their IDs and tactics
    for f in case_study_frequency:
            id = f['id']
            tactic = f['tactic']
            if len(id.split('.')) == 2:
                t = {
                    "techniqueID": id.split('.')[0]+'.'+id.split('.')[1],
                    "score": f['count'],
                    "showSubtechniques": True,
                    "tactic": tactic
                }
            else:
                t = {
                        "techniqueID": id,
                        "score": f['count'],
                        'tactic': tactic
                    }
            ts.append(t)

    # Construct layer data
    case_study_layer_data = {
        "name": name,
        "description": description,
        "techniques": ts,
        "gradient": {
            "colors": [
                "#FFFFFF",
                "#F44336"
            ],
            "minValue": 0,
            "maxValue": len(matrix['case-studies']) # i.e. appears in every study
        },
    }
    # Combine with default layer data
    case_study_layer_data = { **layer_data, **case_study_layer_data}

    # Define output filename
    dir_path = output_dir / layer_output_directory
    case_study_frequency_filename = 'atlas_case_study_frequency.json'
    # Write JSON to file
    write_to_json_file(case_study_layer_data, dir_path, case_study_frequency_filename)

def generate_matrix_layers(matrix, output_dir, matrix_layer_directory='default-navigator-layers'):
    """
    Outputs a layer JSON file highlighting the techniques used in ATLAS
    """

    domain = 'atlas-v2-+-enterprise-v9-atlas'

    # Build mapping of tactic ID to name
    tactic_map = {}
    for tactic in matrix['tactics']:
        tactic_map[tactic['id']] = tactic['name']

    # Base for all layers
    layer_data = {
        "versions": {
            "layer": "4.2",
            "navigator": "4.2"
        },
        "domain": domain,
    }
    # Redefine name and description
    name = "ATLAS Matrix"
    description = "Adversarial Threat Landscape for Artificial-Intelligence Systems, see atlas.mitre.org"

    # Technique highlights
    color = '#C8E6C9'

    # Redefine techniques list
    atlas_matrix_id = []
    for t in matrix['techniques']:
        id_tactic = {}
        if 'AML' in t['id'] and len(t['id'].split('.'))<3:
            # Parent-level technique
            id_tactic['id'] = t['id']

            for tactic in t['tactics']:
                if tactic in tactic_map:
                    # Tactic name with hyphens
                    navigator_tactic = tactic_map[tactic].replace(' ','-').lower()
                    id_tactic['tactic'] = navigator_tactic
                else:
                    raise ValueError(f"Expected to find tactic ID {tactic} in tactic_map")

                # Append a copy of this object
                atlas_matrix_id.append(deepcopy(id_tactic))

        elif 'AML' in t['id']:
            # Subtechnique
            atlas_matrix_id.append({'id': t['id']})

    ts = []
    for id_tactic in atlas_matrix_id:
        id = id_tactic['id']
        if len(id.split('.'))<3:
            tactic = id_tactic['tactic']
            if len(id.split('.')) == 2:
                t = {
                    "techniqueID": id.split('.')[0]+'.'+id.split('.')[1],
                    "color": color,
                    "showSubtechniques": True,
                    "tactic": tactic
                }
        else:
            t = {
                "techniqueID": id,
                "color": color,
            }
        ts.append(t)

    # Construct layer data
    matrix_layer_data = {
        "name": name,
        "description": description,
        "techniques": ts,
        "legendItems": [
            {
                "label": "ATLAS technique",
                "color": color
            }
        ]
    }
    # Combine with default layer data
    matrix_layer_data = { **layer_data, **matrix_layer_data}

    # Define output filename
    dir_path = output_dir / matrix_layer_directory
    matrix_filename = 'atlas_layer_matrix.json'
    # Write JSON to file
    write_to_json_file(matrix_layer_data, dir_path, matrix_filename)

def write_to_json_file(obj, output_dir, filename):
    """Outputs the specified object to JSON file,
    Creates the output directory if not exists.
    """
    # Assumes a Path directory param - if passed a string, convert to a Path
    if not isinstance(output_dir, Path) and isinstance(output_dir, str):
        output_dir = Path(output_dir)

    # Create the output directory if needed, included nested directories
    output_dir.mkdir(parents = True, exist_ok = True)

    # Construct output filepath
    output_filepath = output_dir / filename

    # Write JSON to file
    with open(output_filepath, 'w') as f:
        json.dump(obj, f)

if __name__ == '__main__':
    """Main entry point to ATLAS Navigator layer JSON file generation.

    Uses the ATLAS YAML files from the `data` directory.
    """
    parser = ArgumentParser(
        description = "Creates a Navigator JSON Layer files showing tactics and techniques used by ATLAS."
    )
    # Positional arguments
    parser.add_argument("output_dir",
        type = str,
        help = "Output directory"
    )

    # Input directory
    parser.add_argument("-i", "--input_dir",
        type = str,
        dest = "input_dir",
        default = "data",
        help = "Directory containing YAML data files"
    )
    # Matrix layer gets updated when tactics and techniques change
    # Case study frequency layer and individual layers get updated whenever case studies change
    parser.add_argument("-l", "--layer",
        choices = ['matrix', 'case_study'],
        dest = "layer",
        help = "Output specific layers, otherwise outputs all"
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    # Parse input YAML files into a dictionary
    matrix_filepath = Path(args.input_dir) / 'matrix.yaml'
    _, _, data = load_atlas_data(matrix_filepath)


    if args.layer is None or args.layer == 'matrix':
        # Generate highlight layer that for ATLAS techniques
        generate_matrix_layers(data, output_dir)

    if args.layer is None or args.layer == 'case_study':
        # Generate heatmap layer for techniques in case studies
        generate_case_study_layers(data, output_dir)
        # Generate highlight layer for techniques used in each case study
        generate_individual_case_study_layers(data, output_dir)
