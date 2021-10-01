from copy import deepcopy
from argparse import ArgumentParser
import json
from pathlib import Path
import re

import yaml

from create_matrix import load_atlas_data


"""Converts from AdvML YAML data to STIX."""
# An lowercase, hyphened identifier for this data
SOURCE_NAME = 'mitre-atlas'

def parse_data_files(data_dir_path):
    """Parses the YAML data."""
    data_dir = Path(data_dir_path)
    master = yaml.SafeLoader(data_dir.as_posix())

    # Load the matrix file
    with open(data_dir / 'matrix.yaml', 'r') as f:
        data = yaml_safe_load(f,master=master)
        # TODO Version?
        # construct anchors into dict store and for further parsing
        const = yaml.constructor.SafeConstructor()
        anchors = {k: const.construct_document(v) for k, v in master.anchors.items()}
        # Build flat list of AdvML objects
        case_studies_list=[]
        case_studies_data=data['data'][2]
        for study in case_studies_data:
            for procedure in study['procedure']:
                case_studies_list.append(procedure)
        objects = [object for objects in data["data"] for object in objects]
        # replace all "super aliases" in strings in the document
        objects = walkmap(objects, lambda x: replace_anchors(x, anchors))
        case_studies_list=walkmap(case_studies_list, lambda x: replace_anchors(x, anchors))
        matrix = {
            "tactics": [],
            "techniques": [],
            "case-studies": [],
        }

        # Partition all objects into a dictionary by object type
        for object in objects:
            if object["object-type"] == "technique":
                matrix["techniques"].append(object)
            elif object["object-type"] == "tactic":
                matrix["tactics"].append(object)
            elif object["object-type"] == "case-study":
                matrix["case-studies"].append(object)

    return matrix

def generate_individual_case_study_layers(matrix, individual_case_study_layer_directory):
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
    case_studies=matrix['case-studies']
    # Iterates through each case-study in the matrix file
    for case_study in case_studies:
        # Title at the top of the Navigator tab
        name = case_study['name']
        case_study_id=case_study['id']
        # Appears in layer dropdown
        summary = case_study['summary']
        color = '#C8E6C9'
        # Maps tactic IDs to their name
        tactic_map=[]
        for tactic in matrix['tactics']:
            tactic_map.append({'id':tactic['id'],'name':tactic['name']})
        ts=[]
        # Build dictionary of techniques used in each specific case study
        # These can be a mix of AdvML and ATT&CK techniques
        for t in case_study["procedure"]:
            id=t['technique']
            # changes tactic IDs to their navigator compatible names
            for map in tactic_map:
                if t['tactic'] == map['id']:
                        tactic=map['name'].replace(' ','-').lower()
            # seperates between parent and sub techniques

            if len(id.split('.'))>=3 and id.startswith('AML'):
                short_id=id.split('.')[0]+'.'+id.split('.')[1]
                t={
                    "techniqueID":short_id,
                    "showSubtechniques":True,
                    "tactic":tactic,
                }
                for tss in case_study['procedure']:
                    if short_id== tss['technique'] and short_id not in ts:
                        t={
                            "techniqueID":short_id,
                            "color":color,
                            "showSubtechniques":True,
                            "tactic":tactic,
                        }

                if t not in ts:
                    ts.append(t)
            elif len(id.split('.'))==2 and id.startswith('T'):
                    t={
                        "techniqueID":id.split('.')[0],
                        "showSubtechniques":True,
                        "tactic":tactic,
                    }
                    if t not in ts:
                        ts.append(t)

            t={
                "techniqueID":id,
                "color":color,
                "tactic":tactic,
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
        filename = '{}-case_study_layer.json'.format(case_study_id)
        # Write JSON to file
        write_to_json_file(individual_case_study_layer_data, individual_case_study_layer_directory, filename)

def generate_case_study_layers(matrix, layer_output_directory):
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

    tactic_map=[]
    # creates objects for id's and corresponding tactics
    base_ids = []
    for c in matrix['case-studies']:
        for p in c["procedure"]:
            short_id = deepcopy(p["technique"])
            base_ids.append({
                'id':short_id,
                'tactic':p['tactic'],
                'count':0
            })

    # finds the frequency of each id and it's corresponding tactic
    case_study_frequency=[]
    for group1 in base_ids:
        for group2 in base_ids:
            if group1['id']==group2['id'] and group1['tactic'] == group2['tactic']:
                group1['count']=group1['count']+1
        case_study_frequency.append(group1)

    # Build list of AdvML technique short IDs and associated info
    ts = []
    for tactic in matrix['tactics']:
        tactic_map.append({'id':tactic['id'],'name':tactic['name']})
    print(tactic_map)
   # swaps out tactic id for words from the navigator
    for t in base_ids:
        for map in tactic_map:
            if t['tactic'] == map['id']:
                navigator_tactic=map['name'].replace(' ','-').lower()
                t['tactic']=navigator_tactic
    # creates the list of techniques with their IDs and tactics
    for f in case_study_frequency:
            id=f['id']
            tactic=f['tactic']
            if len(id.split('.'))==2:
                t={
                    "techniqueID":id.split('.')[0]+'.'+id.split('.')[1],
                    "score":f['count'],
                    "showSubtechniques":True,
                    "tactic":tactic
                }
            else:
                t={
                        "techniqueID":id,
                        "score":f['count'],
                        'tactic':tactic
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
    case_study_frequency_filename = 'atlas_case_study_frequency.json'
    # Write JSON to file
    write_to_json_file(case_study_layer_data, layer_output_directory, case_study_frequency_filename)

def generate_matrix_layers(matrix, matrix_layer_directory):
    """
    Outputs a layer JSON file highlighting the frequency of techniques
    used in all of the matrix
    """

    domain = 'atlas-v2-+-enterprise-v9-atlas'
    tactic_map=[]
    for tactic in matrix['tactics']:
        tactic_map.append({'id':tactic['id'],'name':tactic['name']})

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
    advml_matrix_id=[]
    for t in matrix['techniques']:
        id_tactic={}
        if 'AML' in t['id'] and len(t['id'].split('.'))<3:
            id_tactic['id']=t['id']
            for tactic in t['tactics']:
                for map in tactic_map:
                    if tactic == map['id']:
                        navigator_tactic=map['name'].replace(' ','-').lower()
                        id_tactic['tactic']=navigator_tactic
            advml_matrix_id.append(id_tactic)
        elif 'AML' in t['id']:
            advml_matrix_id.append({'id':t['id']})
    ts=[]
    for id_tactic in advml_matrix_id:
            id=id_tactic['id']
            if len(id.split('.'))<3:
                tactic=id_tactic['tactic']
                if len(id.split('.'))==2:
                    t={
                        "techniqueID":id.split('.')[0]+'.'+id.split('.')[1],
                        "color":color,
                        "showSubtechniques":True,
                        "tactic":tactic
                    }
            else:
                t={
                    "techniqueID":id,
                    "color":color,
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
    matrix_filename = 'atlas_layer_matrix.json'
    # Write JSON to file
    write_to_json_file(matrix_layer_data, matrix_layer_directory, matrix_filename)

def write_to_json_file(obj, output_dir, filename):
    """Outputs the specified object to JSON file,
    Creates the output directory if not exists.
    """
    # Assumes a Path directory param - if passed a string, convert to a Path
    if not isinstance(output_dir, Path) and isinstance(output_dir, str):
        output_dir = Path(output_dir)

    # Create the output directory if needed, included nested directories
    output_dir.mkdir(parents=True, exist_ok=True)

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
        description="Creates a Navigator JSON Layer file showing tactics and techniques used by ATLAS."
    )
    parser.add_argument("--dir",
        type=str,
        dest="dir",
        default="data",
        help="Directory containing YAML data files"
    )
    parser.add_argument("--matrix_layer_output",
        type=str,
        dest="matrix_layer_output",
        help='Output directory path for the navigator layer matrix json file to be exported to'
    )
    parser.add_argument("--case_study_layer_output",
        type=str,
        dest="case_study_layer_output",
        help='Output directory path for the navigator layer frequency of case-studies json file to be exported to'
    )
    parser.add_argument("--individual_case_study_layer_output",
        type=str,
        dest="individual_case_study_layer_output",
        help='Output directory path for the navigator layer individual case-study json files to be exported to'
    )

    args = parser.parse_args()

    # Parse input YAML files into a dictionary
    matrix_filepath = Path(args.dir) / 'matrix.yaml'
    _, _, data = load_atlas_data(matrix_filepath)

    # Generate highlight layer that for ATLAS techniques
    if args.matrix_layer_output:
        generate_matrix_layers(data, args.matrix_layer_output)

    # Generate heatmap layer for techniques in case studies
    if args.case_study_layer_output:
        generate_case_study_layers(data, args.case_study_layer_output)

    # Generate highlight layer for techniques used in each case study
    if args.individual_case_study_layer_output:
        generate_individual_case_study_layers(data, args.individual_case_study_layer_output)
