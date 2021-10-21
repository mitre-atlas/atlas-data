import re
import yaml
from argparse import ArgumentParser
import datetime
import os
from schema import Schema, Or, Optional
import itertools
import pprint
import json


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        nargs=1,
        action="store",
        default=["console"],
        help="input a text file name to hold the faulty objects from the matrix",
    )
    parser.add_argument("--matrix", "-m", type=str, default="data/matrix.yaml")
    args = parser.parse_args()
    file_name = args.file[0]

    wd = os.getcwd()
    os.chdir(os.path.dirname(args.matrix))
    matrix_filename = os.path.basename(args.matrix)

    # load yaml with custom loader that supports !include and cross-doc anchors
    master = yaml.SafeLoader("")
    with open(matrix_filename, "rb") as f:
        data = yaml_safe_load(f, master=master)

    # load yaml with custom loader that supports !include and cross-doc anchors
    master = yaml.SafeLoader("")
    with open(matrix_filename, "rb") as f:
        data = yaml_safe_load(f, master=master)

    # construct anchors into dict store and for further parsing
    const = yaml.constructor.SafeConstructor()
    anchors = {k: const.construct_document(v) for k, v in master.anchors.items()}

    # flatten the objects list of lists
    objects = [object for objects in data["data"] for object in objects]

    # handling for if name/id is misspelled
    try:
        # replace all "super aliases" in strings in the document
        objects = walkmap(objects, lambda x: replace_anchors(x, anchors))
    except:
        print(end="")

    # organize objects into dicts by object-type
    # and make sure techniques are in the order defined in the matrix
    matrix = {
        "tactics": data["tactics"],
        "techniques": [],
        "case-studies": [],
    }

    for object in objects:
        # ensuring that object-type is spelled properly
        if "object-type" in object and "id" in object:
            if object["id"] != None:
                if object["object-type"] == "technique":
                    # checks to see if id is correct
                    if object["id"].startswith("AML") or object["id"].startswith("T"):
                        matrix["techniques"].append(object)
                    else:
                        errormsg(object, file_name, "technique id error")
                elif object["object-type"] == "tactic":
                    if object["id"].startswith("AML") or object["id"].startswith("T"):
                        idx = matrix["tactics"].index(object["id"])
                        matrix["tactics"][idx] = object
                    else:
                        errormsg(object, file_name, "tactic id error")
                elif object["object-type"] == "case-study":
                    if object["id"].startswith("AML") or object["id"].startswith("T1"):
                        matrix["case-studies"].append(object)
                    else:
                        errormsg(object, file_name, "case-study id error")
                # handling for if object-type value is missing
                elif object["object-type"] == None:
                    errormsg(object, file_name, "object-type missing")
                    # handling for if object-type value is not a string
                else:
                    errormsg(object, file_name, "incompatible object-type")
            else:
                errormsg(object, file_name, "missing id")
        elif "object-type" not in object:
            errormsg(object, file_name, "error with object-type spelling")
        elif "id" not in object:
            errormsg(object, file_name, "error with id spelling")

    def check_structure(struct, conf):
        if isinstance(struct, dict) and isinstance(conf, dict):
            # struct is a dict of types or other dicts
            return all(
                k in conf and check_structure(struct[k], conf[k]) for k in struct
            )
        if isinstance(struct, list) and isinstance(conf, list):
            # struct is list in the form [type or dict]
            return all(check_structure(struct[0], c) for c in conf)
        elif isinstance(struct, type):
            # struct is the type of conf
            return isinstance(conf, struct)
        else:
            # struct is neither a dict, nor list, not type
            return False

    # validate setup of matrix
    matrix_schema = Schema({"case-studies": list, "tactics": list, "techniques": list})
    print("\033[1mMatrix Validity:\033[0m")
    print(matrix_schema.is_valid(matrix))

    # validate all case studies
    case_study_schema = Schema(
        {
            "id": str,
            "name": str,
            "object-type": str,
            "summary": str,
            "incident-date": datetime.date,
            "dateGranularity": str,
            "procedure": list,
            "reported-by": str,
            Optional("references"): Or(list, None),
        }
    )
    print("\033[1mCase-study Validity:\033[0m")
    print_results(
        test_validity(matrix["case-studies"], case_study_schema, file_name, errormsg)
    )

    # validate all tactics
    tactics_schema = Schema(
        {
            "description": str,
            "id": str,
            "name": str,
            "object-type": str,
        }
    )
    print("\033[1mTactics Validity:\033[0m")
    print_results(test_validity(matrix["tactics"], tactics_schema, file_name, errormsg))

    # validate techniques
    techniques_schema = Schema(
        {
            "id": str,
            "object-type": Or("tactic", "technique", "case-study"),
            "name": str,
            "description": str,
            Optional("tactics"): list,
            Optional("subtechnique-of"): str,
        }
    )
    print("\033[1mTechniques Validity:\033[0m")
    print_results(
        test_validity(matrix["techniques"], techniques_schema, file_name, errormsg)
    )

    # validate procedure
    procedure_schema = Schema({"tactic": str, "technique": str, "description": str})
    print("\033[1mProcedures Validity:\033[0m")
    procedure_validity = []
    for casestudy in matrix["case-studies"]:
        procedure_validity.append(
            test_validity(casestudy["procedure"], procedure_schema, file_name, errormsg)
        )
    print_results(list(itertools.chain(*procedure_validity)))

    # validate references
    references_schema = Schema(
        {
            "sourceDescription": Or(str, None),
            "url": Or(str, None),
        }
    )
    print("\033[1mReferences Validity:\033[0m")
    references_validity = []
    for casestudy in matrix["case-studies"]:
        if "references" in casestudy:
            try:
                if casestudy["references"]:
                    references_validity.append(
                        test_validity(
                            casestudy["references"],
                            references_schema,
                            file_name,
                            errormsg,
                        )
                    )
            except:
                print(f"Invalid 'references' format for {casestudy['id']}")
                references_validity.append([False])
    print_results(list(itertools.chain(*references_validity)))

    # check for balanced parentheses in case-studies
    print("\033[1mCase-study Parentheses Balance:\033[0m")
    print_results(balanced_parentheses(matrix["case-studies"], file_name, errormsg))

    # check for balanced parentheses in tactics
    print("\033[1mTactic Parentheses Balance:\033[0m")
    print_results(balanced_parentheses(matrix["tactics"], file_name, errormsg))

    # check for balanced parentheses in techniques
    print("\033[1mTechniques Parentheses Balance:\033[0m")
    print_results(balanced_parentheses(matrix["techniques"], file_name, errormsg))

    # check for balanced parentheses in procedures
    print("\033[1mProcedure Parentheses Balance:\033[0m")
    procedure_parentheses_balance = []
    for casestudy in matrix["case-studies"]:
        procedure_parentheses_balance.append(
            balanced_parentheses(casestudy["procedure"], file_name, errormsg)
        )
    print_results(list(itertools.chain(*procedure_validity)))

    os.chdir(wd)


def balanced_parentheses(matrix_section, file_name, errormsg):
    pp = pprint.PrettyPrinter(indent=4)
    """
    iterates through objects in specified matrix section to check for matching opening
    and closing parentheses using the check(str) function
    """
    balanced = []
    for index, obj in enumerate(matrix_section):
        balanced.append(check(str(obj)))
        if check(str(obj)) == False:
            errorstr = "Error with Object #{}."
            errormsg(obj, file_name, errorstr.format(index))
    return balanced


# Function to check parentheses adapted from https://www.geeksforgeeks.org/check-for-balanced-parentheses-in-python/
def check(myStr):
    open_list = ["[", "{", "("]
    close_list = ["]", "}", ")"]
    stack = []
    for i in myStr:
        if i in open_list:
            stack.append(i)
        elif i in close_list:
            pos = close_list.index(i)
            if (len(stack) > 0) and (open_list[pos] == stack[len(stack) - 1]):
                stack.pop()
            else:
                return False
    if len(stack) == 0:
        return True
    else:
        return False


def errormsg(objoutput, file_name, errorstr=""):
    """
    prints error to the console by default or to a file specified by the user
    """
    pp = pprint.PrettyPrinter(indent=4)
    if file_name == "console":
        print(errorstr)
        pp.pprint(objoutput)
    elif file_name != "console":
        f = open(file_name, "a")
        print(errorstr)
        f.write(json.dumps(objoutput, indent=4))
        f.close()


def test_validity(matrix_section, schema, file_name, errormsg):
    """
    iterates through objects in specified matrix section to check for proper format of keys and value
    types based on their specific schemas
    """
    correctness = []
    for index, obj in enumerate(matrix_section):
        correctness.append(schema.is_valid(obj))
        if schema.is_valid(obj) == False:
            errorstr = "Error with Object #{}."
            errormsg(obj, file_name, errorstr.format(index))
    return correctness


def print_results(test_results):
    """
    prints the results of each test to the console
    """
    if False in test_results and True not in test_results:
        print("False")
    if False in test_results and True in test_results:
        print("The rest are true")
    if False not in test_results and True in test_results:
        print("True")


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
    matches = re.findall("{{\s*(.*?)\s*}}", x, re.DOTALL)
    for match in matches:
        val = objget(anchors, match)
        x = re.sub(f"{{{{\s*{match}\s*}}}}", f"{val}", x, re.DOTALL)
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
