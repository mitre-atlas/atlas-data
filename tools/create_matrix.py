from argparse import ArgumentParser
import os
from pathlib import Path

from jinja2 import Environment
import yaml

"""
Creates the combined ATLAS YAML file from source data.
"""


def main():
    parser = ArgumentParser()
    parser.add_argument("--matrix", "-m", type=str, default="data/matrix.yaml", help="Path to matrix.yaml")
    parser.add_argument("--output", "-o", type=str, default=".", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    matrix = load_atlas_data(args.matrix)

    # save composite document as a standard yaml file
    output = os.path.join(args.output, f"{matrix['id']}.yaml")
    with open(output, "w") as f:
        yaml.dump(matrix, f, default_flow_style=False, explicit_start=True, sort_keys=False)

def load_atlas_data(matrix_yaml_filepath):
    """Returns a dictionary representing ATLAS data
    as read from the provided YAML files.
    """
    wd = os.getcwd()
    os.chdir(os.path.dirname(matrix_yaml_filepath))

    # load yaml with custom loader that supports !include and cross-doc anchors
    master = yaml.SafeLoader("")
    with open(os.path.basename(matrix_yaml_filepath), "rb") as f:
        data = yaml_safe_load(f, master=master)

    # construct anchors into dict store and for further parsing
    const = yaml.constructor.SafeConstructor()
    anchors = {k: const.construct_document(v) for k, v in master.anchors.items()}

    ## Jinja template evaluation

    # Use YAML default style of literal string "" wrappers to handle apostophes/single quotes in the text
    data_str = yaml.dump(data, default_flow_style=False, sort_keys=False, default_style='"')
    # Set up data as Jinja template
    env = Environment()
    template = env.from_string(data_str)
    # Validate template - throws a TemplateSyntaxError if invalid
    env.parse(template)

    # Replace all "super aliases" in strings in the document
    populated_data_str = template.render(anchors)
    # Convert populated data string back to a dictionary
    data = yaml.safe_load(populated_data_str)

    ## Construct output format

    # Objects are lists of lists under 'data' as !includes are list items
    # Flatten the objects
    objects = [object for objects in data["data"] for object in objects]

    # organize objects into dicts by object-type
    # and make sure tactics are in the order defined in the matrix
    matrix = {
        "id": data["id"],
        "name": data["name"],
        "version": data["version"],
        "tactics": data["tactics"],
        "techniques": [],
        "case-studies": []
    }
    for object in objects:
        if object["object-type"] == "technique":
            matrix["techniques"].append(object)
        elif object["object-type"] == "tactic":
            if object["id"] in matrix["tactics"]:
                idx = matrix["tactics"].index(object["id"])
                matrix["tactics"][idx] = object
        elif object["object-type"] == "case-study":
            matrix["case-studies"].append(object)

    os.chdir(wd)

    return matrix

#region Support !include in YAML

# taken from
# https://stackoverflow.com/questions/44910886/pyyaml-include-file-and-yaml-aliases-anchors-references

# allow for cross-document anchors
def compose_document(self):
    self.get_event()
    node = self.compose_node(None, None)
    self.get_event()
    # self.anchors = {}    # <<<< commented out
    return node


yaml.SafeLoader.compose_document = compose_document

# add !include constructor
# adapted from http://code.activestate.com/recipes/577613-yaml-include-support/
def yaml_include(loader, node):
    # Process input argument
    # node.value is assumed to be a relative filepath that may include wildcards
    has_wildcard = '*' in node.value
    include_path = Path(node.value)
    # Split path into its parts
    include_path_parts = include_path.parts
    # Number includes directories and the file/pattern itself
    has_directory = len(include_path_parts) > 1

    # Validate inputs
    if include_path.suffix not in ['.yaml', '.yml']:
        # Check file extension
        raise ValueError(f'Expected !include path to end in .yaml or .yml, got "{node.value}" ending in "{include_path.suffix}"')
    if not has_wildcard and not include_path.exists():
        # Specified file does not exist
        raise FileNotFoundError(node.value)

    # Construct outputs
    # Note that both approaches, returning a self-constructed list for wildcards
    # and returning a document of lists results in the same 2x nested list format
    # which is why nested lists are flattened in load_atlas_data

    if has_wildcard:
        # Collect documents into a single array
        results = []
        # Get all matching files from the current working directory
        filepaths = Path.cwd().glob(node.value)
        # Read in each file in name-order and append to results
        for filepath in sorted(filepaths):
            with open(filepath) as inputfile:
                result = yaml_safe_load(inputfile, master=loader)
                results.append(result)

        return results

    else:
        # Return specified document
        with open(node.value) as inputfile:
            return yaml_safe_load(inputfile, master=loader)


yaml.add_constructor("!include", yaml_include, Loader=yaml.SafeLoader)


def yaml_safe_load(stream, Loader=yaml.SafeLoader, master=None):
    loader = Loader(stream)
    if master is not None:
        loader.anchors = master.anchors
    try:
        return loader.get_single_data()
    finally:
        loader.dispose()

#endregion

if __name__ == "__main__":
    main()
