import os
import re
import yaml
from argparse import ArgumentParser


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

    # flatten the objects list of lists
    objects = [object for objects in data["data"] for object in objects]

    # replace all "super aliases" in strings in the document
    objects = walkmap(objects, lambda x: replace_anchors(x, anchors))
    tactics = walkmap(data["tactics"], lambda x: replace_anchors(x, anchors))

    # organize objects into dicts by object-type
    # and make sure techniques are in the order defined in the matrix
    matrix = {
        "id": data["id"],
        "name": data["name"],
        "version": data["version"],
        "tactics": tactics,
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

def objget(x, path, sep="."):
    """
    traverses object 'x' (nested indexible objects) according to path
    converts indices to ints if they are digits
    """

    if sep in path:
        path, rest = path.split(sep, 1)
        path = int(path) if path.isdigit() else path
        return objget(x[path], rest)
    elif len(path) > 0:
        path = int(path) if path.isdigit() else path
        return x[path]
    else:
        return x


def walkmap(x, f, types=str):
    """
    recursively walks an an an object 'x' of nested dicts/lists/tuples
    and applies function 'f' to all objects of types 'types'
    """

    if isinstance(x, dict):
        x = {k: walkmap(v, f, types) for k, v in x.items()}
    elif isinstance(x, list) or isinstance(x, tuple):
        x = [walkmap(v, f, types) for v in x]
    elif isinstance(x, types):
        x = f(x)
    return x


def replace_anchors(x, anchors):
    """
    replaces aliases (denoted by '{{ }}') in 'x' with its anchor in 'anchors'
    hacky: right now assumes the anchor is a dict and the alias is referencing a scalar value in that dict
    """

    matches = re.findall(r"{{\s*(.*?)\s*}}", x, re.DOTALL)
    for match in matches:
        val = objget(anchors, match)
        x = re.sub(rf"{{{{\s*{match}\s*}}}}", f"{val}", x, re.DOTALL)
    return x


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


if __name__ == "__main__":
    main()
