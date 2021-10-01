from copy import deepcopy
from argparse import ArgumentParser
import json
from pathlib import Path
import re

import requests
from stix2 import Filter, MemoryStore, properties
from stix2.v20 import AttackPattern, Bundle, CustomObject, ExternalReference, KillChainPhase, Relationship
import yaml

from create_matrix import load_atlas_data

"""
Custom MITRE ATT&CK STIX object to be able to use the Navigator - need the matrix custom object.
        https://github.com/mitre/cti/blob/master/USAGE.md#the-attck-data-model
        https://stix2.readthedocs.io/en/latest/guide/custom.html?highlight=custom#Custom-STIX-Object-Types
    To my knowledge, these don't exist in a script or library...
"""
@CustomObject('x-mitre-tactic', [
    ('name', properties.StringProperty()),
    ('description', properties.StringProperty()),
    # https://github.com/oasis-open/cti-python-stix2/blob/master/stix2/properties.py#L197
    ('external_references', properties.ListProperty(ExternalReference)),
    # Custom tactic not showing up in Navigator - adding these properties for completeness
    # but they have no effect - might be v2.1 vs. 2.0
    ('x_mitre_shortname', properties.StringProperty()),
    ('created_by_ref', properties.StringProperty()),
    ('object_marking_refs', properties.ListProperty(properties.StringProperty))
])
class AttackTactic():
    """Custom MITRE ATT&CK tactic STIX object."""
    def __init__(self, **kwargs):
        pass

@CustomObject('x-mitre-matrix', [
    ('name', properties.StringProperty()),
    ('description', properties.StringProperty()),
    # https://github.com/oasis-open/cti-python-stix2/blob/master/stix2/properties.py#L197
    ('external_references', properties.ListProperty(ExternalReference)),
    ('tactic_refs', properties.ListProperty(properties.StringProperty))
])
class AttackMatrix():
    """Custom MITRE ATT&CK matrix STIX object."""
    def __init__(self, **kwargs):
        pass


class AttackDataParser():
    """Accesses ATT&CK Enterprise data."""

    # Filters for ATT&CK data
    TACTIC_FILTER = Filter('type', '=', 'x-mitre-tactic')

    def __init__(self):
        # Retrieve raw JSON from GitHub
        attack_enterprise_json = 'https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json'
        self.stix_json = requests.get(attack_enterprise_json).json()
        # Load into STIX memory store for later parsing
        self.attack_memory_store = MemoryStore(stix_data=self.stix_json["objects"])

        # Set references for object creation
        self.identity = self.get_mitre_identity()
        self.marking_definition = self.get_marking_copyright()
        self.object_marking_refs = [
            self.marking_definition['id']
        ]

    def build_tactic_id_filter(self, tactic_id):
        """Returns a STIX Filter for the specified ID, usually as the first item in a tactic's references."""
        return Filter('external_references.external_id', '=', tactic_id)

    def get_tactic(self, tactic_id):
        """Returns the lowercase name of the specified tactic, for use by Kill Chain Phase."""
        # Find tactics with this ID
        matching_tactics = self.attack_memory_store.query([
            AttackDataParser.TACTIC_FILTER,
            self.build_tactic_id_filter(tactic_id)
        ])

        # There should only be one
        assert(len(matching_tactics) == 1)

        # Use lowercase version of tactic name, to fit Kill Chain Phase specs
        tactic = matching_tactics[0]
        tactic_name = tactic['x_mitre_shortname']

        return tactic, tactic_name

    def get_matrix(self):
        """Returns the x-mitre-matrix object."""
        matching_items = self.attack_memory_store.query([
            Filter('type', '=', 'x-mitre-matrix')
        ])

        # There should only be one
        assert(len(matching_items) == 1)

        return matching_items[0]

    def get_mitre_identity(self):
        """Returns the identity representing The MITRE Corporation."""
        matching_items = self.attack_memory_store.query([
            Filter('name', '=', 'The MITRE Corporation')
        ])

        # There should only be one
        assert(len(matching_items) == 1)

        return matching_items[0]

    def get_marking_copyright(self):
        """Returns the copyright statement that makes up every object marking ref."""
        matching_items = self.attack_memory_store.query([
            Filter('type', '=', 'marking-definition')
        ])

        # There should only be one
        assert(len(matching_items) == 1)

        return matching_items[0]


class AdvML:
    """Converts from AdvML YAML data to STIX."""
    # An lowercase, hyphened identifier for this data
    SOURCE_NAME = 'mitre-atlas'

    def __init__(self, data_dir_path, use_advml_relevant_only=True):
        """Initialize an AdvML object.  Defaults provided via arguments in main.

        Args:
            data_dir_path (str): Path to the data directory
            use_advml_relevant_only (bool): Whether to use AdvML and only relevant ATT&CK entries (True),
                or AdvML and all of ATT&CK Enterprise
        """
        self.attack_data_parser = AttackDataParser()
        self.parse_data_files(data_dir_path)
        # Track referenced ATT&CK tactics by short ID
        self.referenced_attack_tactics = {}
        # Track AdvML (and later combine with ATT&CK) tactics by short ID
        # for matrix ordering lookup
        self.tactic_mapping = {}
        self.use_advml_relevant_only = use_advml_relevant_only

    def parse_data_files(self, data_dir_path):
        """Parses the YAML data and sets attributes."""
        matrix_filepath = Path(data_dir_path) / 'matrix.yaml'
        self.matrix_name, _, matrix = load_atlas_data(matrix_filepath)

        self.tactics = matrix["tactics"]
        self.techniques = matrix["techniques"]
        self.studies = matrix["case-studies"]

    def to_stix_json(self, stix_output_filepath, advml_url):
        """Saves a STIX JSON file of the AdvML tactics and techniques info,
        populated from ATT&CK Enterprise where needed.

        STIX Bundle specs
        https://docs.oasis-open.org/cti/stix/v2.1/cs01/stix-v2.1-cs01.html#_nuwp4rox8c7r
        """

        # Convert AdvML techniques first to populate the referenced ATT&CK tactics
        # Only for parent techniques, as subtechniques do not have tactics references
        # TODO Is it an invariant that subtechniques always follow their parent techniques?
        # TODO No, broken with Tainting Data from Acquisition - Label Corruption referencing T0019 but following T0018 - manually changing
        stix_techniques = []
        relationships = []
        parent_technique = None
        for t in self.techniques:
            if 'subtechnique-of' in t:
                pass
                # Create subtechnique and relationship
                subtechnique, relationship = self.subtechnique_to_attack_pattern(t, parent_technique, advml_url)
                # Add to trackers
                stix_techniques.append(subtechnique)
                relationships.append(relationship)
            else:
                # Create and add this technique
                technique = self.technique_to_attack_pattern(t, advml_url)
                stix_techniques.append(technique)
                # Save off reference to this technique for use by its subtechniques, should there be any following
                parent_technique = technique

        # stix_techniques = [self.technique_to_attack_pattern(t, advml_url) for t in self.techniques if 'subtechnique-of' not in t]
        print(f'Converted {len(stix_techniques)} AdvML techniques to STIX objects.')
        print(f'\t{len(relationships)} subtechnique relationships.')

        # Convert AdvML tactics to x-mitre-tactics
        stix_tactics = [self.tactic_to_mitre_attack_tactic(t, advml_url) for t in self.tactics]
        print(f'Converted {len(stix_tactics)} AdvML tactics to STIX objects.')
        # Add any referenced ATT&CK tactics, otherwise they'll already exist in the full ATT&CK
        if self.use_advml_relevant_only:
            stix_tactics.extend(self.referenced_attack_tactics.values())

        # Build x-mitre-matrix

        # TODO - should this be part of matrix.yaml?
        matrix_description = ''

        # Controls location of "View tactic/technique" on Navigator item right-click
        external_references = [
            ExternalReference(
                source_name = AdvML.SOURCE_NAME,
                url=advml_url
            )
        ]

        # Build ordered list of tactics
        tactic_refs = []
        if self.use_advml_relevant_only:
            # Combine short ID-to-STIX tactic dictionaries to populate the matrix tactics in order
            self.tactic_mapping.update(self.referenced_attack_tactics)
            # Order of tactics in matrix, by STIX ID reference
            # tactic_refs = [self.tactic_mapping[tactic_id]['id'] for tactic_id in self.matrix_tactic_id_order]
        else:
            # Find the AdvML tactics and their preceding ATT&CK IDs
            # Insert the custom tactics

            # Find the existing x-mitre-matrix object from ATT&CK Enterprise
            attack_matrix = self.attack_data_parser.get_matrix()
            attack_tactic_refs = attack_matrix['tactic_refs']

            # TODO Check if this works
            prev_tactic_short_id = None
            for tactic_short_id in self.matrix_tactic_id_order:

                if tactic_short_id.startswith('AML.TA'):
                    # Retrieve the ATT&CK tactic by short ID
                    prev_tactic_stix, _ = self.attack_data_parser.get_tactic(prev_tactic_short_id)
                    # Find the index of this ATT&CK tactic
                    prev_tactic_stix_index = attack_tactic_refs.index(prev_tactic_stix['id'])
                    # Look up the STIX ID of this AdvML tactic
                    tactic_stix_id = self.tactic_mapping[tactic_short_id]['id']
                    # Insert the AdvML STIX tactic right after the ATT&CK one
                    attack_tactic_refs.insert(prev_tactic_stix_index + 1, tactic_stix_id)

                # Continue tracking the previous short ID
                prev_tactic_short_id = tactic_short_id

            # Update the tactic refs
            tactic_refs = attack_tactic_refs

        print(f'Generated {len(tactic_refs)} tactic references for the AdvML matrix object.')

        stix_matrix_obj = AttackMatrix(
            name=self.matrix_name,
            description=matrix_description,
            external_references=external_references,
            tactic_refs=tactic_refs
        )

        # JSON
        stix_json = None

        if self.use_advml_relevant_only:
            print('Bundling and serializing ATLAS data to JSON file...')
            bundle = Bundle(
                objects=stix_tactics + stix_techniques + relationships + [stix_matrix_obj],
                allow_custom=True # Needed as ATT&CK data has custom objects
            )
            stix_json = json.loads(bundle.serialize())

        else:
            """
            print('Adding AdvML-specific STIX objects to the ATT&CK memory store...')
            # Add AdvML tactics
            self.attack_data_parser.attack_memory_store.add(stix_tactics)
            # Add AdvML techniques
            self.attack_data_parser.attack_memory_store.add(stix_techniques)
            # Add subtechnique relationships
            self.attack_data_parser.attack_memory_store.add(relationships)
            # Add combined matrix to the memory store
            self.attack_data_parser.attack_memory_store.add(stix_matrix_obj)

            # TODO Remove the existing ATT&CK matrix object
            # Currently manually removed from the resulting JSON file

            print('Saving the memory store to JSON file...')
            self.attack_data_parser.attack_memory_store.save_to_file(stix_output_filepath)
            """

            # Get all ATT&CK objects except for the matrix definition
            attack_objs = [obj for obj in self.attack_data_parser.stix_json['objects'] if obj['type'] != 'x-mitre-matrix' ]
            # Add to the ATLAS bundle
            bundle = Bundle(
                objects=stix_tactics + stix_techniques + relationships + [stix_matrix_obj] + attack_objs,
                allow_custom=True # Needed as ATT&CK data has custom objects
            )
            stix_json = json.loads(bundle.serialize())

        # Save to file
        with open(stix_output_filepath, 'w') as f:
            json.dump(stix_json, f)
            print('Done!')

    def referenced_tactics_to_kill_chain_phases(self, tactic_ids):
        """Converts a list of tactic IDs referenced by a technique
        to a list of STIX Kill Chain Phases.

        Kill Chain Phase spec:
        https://docs.oasis-open.org/cti/stix/v2.1/cs01/stix-v2.1-cs01.html#_i4tjv75ce50h
        """
        kill_chain_phases = []

        for tactic_id in tactic_ids:
            # Default properies, if not recognized as AdvML or ATT&CK
            # TODO Model Poisoning & Tainting Data from Acquisition - Label Corruption had this as a 2nd tactic - why? Manually replacing
            kill_chain_name= '?'
            phase_name = '?'

            if tactic_id.startswith('AML.TA'):
                # AdvML
                kill_chain_name = AdvML.SOURCE_NAME # Using this as an identifier

                # Look up AdvML tactic name
                tactic = next((tactic for tactic in self.tactics if tactic['id'] == tactic_id), None)
                # Ensure this is found
                assert(tactic is not None)
                # Convert name to lowercase and hyphens to fit spec
                phase_name = tactic['name'].lower().replace(' ', '-')

            elif tactic_id.startswith('TA'):
                # ATT&CK
                kill_chain_name = 'mitre-attack'

                # Look up ATT&CK tactic and lowercase hyphenated name to use as phase name
                tactic, phase_name = self.attack_data_parser.get_tactic(tactic_id)

                # Keep track of unique tactic objects
                if tactic_id not in self.referenced_attack_tactics:
                    self.referenced_attack_tactics[tactic_id] = tactic

            # Create and add
            kcp = KillChainPhase(
                kill_chain_name=kill_chain_name,
                phase_name=phase_name
            )
            kill_chain_phases.append(kcp)

        return kill_chain_phases

    def build_advml_external_references(self, t, advml_url, route='techniques'):
        """Returns a STIX External Reference for AdvML data."""

        # Construct the full URL to the resource
        url = advml_url + '/' + route + '/' + t['id']

        # External references is a list
        return [
            ExternalReference(
                source_name=AdvML.SOURCE_NAME, # The only required property
                url=url,
                external_id=t['id']
            )
        ]

    def tactic_to_mitre_attack_tactic(self, t, advml_url):
        """Returns a STIX x-mitre-tactic representing this tactic."""
        at = AttackTactic(
            name=t['name'],
            description=t['description'],
            external_references=self.build_advml_external_references(t, advml_url, 'tactics'),
            x_mitre_shortname=t['name'].lower().replace(' ','-'),
            created_by_ref=self.attack_data_parser.identity['id'],
            object_marking_refs=self.attack_data_parser.object_marking_refs
        )

        # Track this tactic by short ID
        self.tactic_mapping[t['id']] = at

        return at

    def technique_to_attack_pattern(self, t, advml_url):
        """Returns a STIX AttackPattern representing this technique."""
        return AttackPattern(
            name=t['name'],
            description=t['description'],
            kill_chain_phases=self.referenced_tactics_to_kill_chain_phases(t['tactics']),
            external_references=self.build_advml_external_references(t, advml_url),
            # Needed by Navigator else TypeError technique.platforms is not iterable
            allow_custom=True,
            x_mitre_platforms=['ATLAS']
        )

    def subtechnique_to_attack_pattern(self, t, parent, advml_url):
        """Returns a STIX AttackPattern representing this subtechnique and a STIX Relationship
        between this subtechnique and its parent.

        https://github.com/mitre/cti/blob/master/USAGE.md#sub-techniques
        """
        subtechnique = AttackPattern(
            name=t['name'],
            description=t['description'],
            kill_chain_phases=parent.kill_chain_phases,
            external_references=self.build_advml_external_references(t, advml_url),
            # Needed by Navigator else TypeError technique.platforms is not iterable
            allow_custom=True,
            x_mitre_platforms=['ATLAS'],
            x_mitre_is_subtechnique=True
        )

        relationship = Relationship(
            source_ref=subtechnique.id,
            relationship_type='subtechnique-of',
            target_ref=parent.id
        )

        return subtechnique, relationship


if __name__ == '__main__':
    """Main entry point to STIX and layer JSON file generation for
    either ATLAS-related or full ATT&CK Enterprise + ATLAS data.

    Uses the ATLAS YAML files from the `data` project, as well as
    ATT&CK Enterprise data as pulled from GitHub.

    Note that the full/all option runs for a while and produces a 13-16 MB file
    depending on whether indents exist.

    Uncomment the lines at the bottom.
    """
    parser = ArgumentParser(
        description="Creates a STIX JSON file showing tactics and techniques used by ATLAS."
    )
    parser.add_argument("--dir",
        type=str,
        dest="dir",
        default="data",
        help="Directory containing YAML data files"
    )
    parser.add_argument("--url",
        type=str,
        dest="advml_url",
        default="https://atlas.mitre.org",
        help="URL to AdvML website for Navigator item linking"
    )
    parser.add_argument("--stix_out",
        type=str,
        dest="stix_output_filepath",
        default="atlas-stix.json",
        help="Output filepath for STIX JSON"
    )
    parser.add_argument("--all",
        action="store_true",
        help="Includes all from ATT&CK Enterprise"
    )

    args = parser.parse_args()

    advml = AdvML(
        data_dir_path=args.dir,
        use_advml_relevant_only=not args.all
    )

    # Convert to and save STIX
    advml.to_stix_json(args.stix_output_filepath, args.advml_url)

    """
    Layer displaying ATLAS

    {
        "name": "ATLAS Matrix",
        "versions": {
            "layer": "4.2",
            "navigator": "4.2"
        },
        "description": "Adversarial Machine Learning",
        "domain": "atlas-v2-+-enterprise-v9-atlas",
        "filters": {
            "platforms": [
                "ATLAS"
            ]
        }
    }
    """
