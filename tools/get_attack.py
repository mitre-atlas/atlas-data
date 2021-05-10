import os
import yaml
import requests
from argparse import ArgumentParser

"""
Downloads and parses the ATT&CK enterprise data.
Extracts objects relevant to the AdvML Threat Matrix.
Converts the data objects to the Advml format.
Saves output as a YAML file.
"""


def main():
    parser = ArgumentParser()
    parser.add_argument("--version", "-v", type=str, default="9.0")
    args = parser.parse_args()

    attack_url = f"https://github.com/mitre/cti/raw/ATT%26CK-v{args.version}/enterprise-attack/enterprise-attack.json"

    data = load_attack(attack_url)
    attack = parse_attack(data)

    with open(f"enterprise-attack-{args.version}.yaml", "w") as f:
        yaml.dump(attack, f, default_flow_style=False, explicit_start=True)


def load_attack(uri: str) -> dict:
    # load full STIX JSON data
    if os.path.exists(uri):
        with open(uri, "rb") as f:
            data = json.load(f)
    else:  # assume url
        data = requests.get(uri).json()

    return data


def parse_attack_id(object: dict) -> str:
    """
    Extract the object's external ID
    """

    for ref in object["external_references"]:
        if ref["source_name"] == "mitre-attack":
            return ref["external_id"]

    return None


def parse_attack(data: str) -> list:
    """
    Parse ATT&CK STIX JSON into a list of tactic and technique objects.
    """

    attack = dict(
        {
            "tactics": {},
            "techniques": {},
        }
    )

    uuid_to_id = {}
    subt_uuid_to_tech_uuid = {}
    tech_id_to_tactic_names = {}
    tactic_name_to_tactic_id = {}
    for object in data["objects"]:
        # skip over any revoked objects
        if object.get("revoked", False):
            continue

        object_type = {
            "x-mitre-tactic": "tactic",
            "attack-pattern": "technique",
        }.get(object["type"], None)

        if object_type is not None:
            id = parse_attack_id(object)
            uuid_to_id[object["id"]] = id

            description = object["description"].replace("https://attack.mitre.org", "")

            advml_object = {
                "id": id,
                "object-type": object_type,
                "name": object["name"],
                "description": description,
            }

            if object["type"] == "attack-pattern":
                tactic_names = [
                    phase["phase_name"] for phase in object["kill_chain_phases"]
                ]
                tech_id_to_tactic_names[id] = tactic_names
                advml_object["object-type"] = "technique"
                attack["techniques"][id] = advml_object

            elif object["type"] == "x-mitre-tactic":
                tactic_name_to_tactic_id[object["x_mitre_shortname"]] = id
                advml_object["object-type"] = "tactic"
                attack["tactics"][id] = advml_object

        # record subtechnique relationships
        elif object["type"] == "relationship":
            if object["relationship_type"] == "subtechnique-of":
                subt_uuid_to_tech_uuid[object["source_ref"]] = object["target_ref"]

    # add subtechnique relationships
    for subt_uuid, tech_uuid in subt_uuid_to_tech_uuid.items():
        subt_id = uuid_to_id[subt_uuid]
        tech_id = uuid_to_id[tech_uuid]
        attack["techniques"][subt_id]["subtechnique-of"] = tech_id

    # add tactic ids to techniques
    for tech_id, tactic_names in tech_id_to_tactic_names.items():
        if "subtechnique-of" in attack["techniques"][tech_id]:
            continue
        tactic_ids = [tactic_name_to_tactic_id[n] for n in tactic_names]
        attack["techniques"][tech_id]["tactics"] = tactic_ids

    objects = []
    objects.extend([obj for obj in attack["tactics"].values()])
    objects.extend([obj for obj in attack["techniques"].values()])

    return objects


if __name__ == "__main__":
    main()
