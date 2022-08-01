import datetime

import pytest
from schema import Or, Optional, Regex, Schema

from schemas import atlas_matrix, atlas_obj
from tools.create_matrix import load_atlas_data

"""
Defines global pytest fixtures for ATLAS data and schemas.

This file is in the top-level of the repo for access to tools and schemas.

https://docs.pytest.org/en/6.2.x/fixture.html#conftest-py-sharing-fixtures-across-multiple-files
"""

#region Parameterized fixtures
@pytest.fixture(scope='session')
def output_data(request):
    """Represents the ATLAS output data (ATLAS.yaml) dictionary."""
    return request.param

@pytest.fixture(scope='session')
def matrix(request):
    """Represents the ATLAS matrix dictionary."""
    return request.param

@pytest.fixture(scope='session')
def tactics(request):
    """Represents each tactic dictionary."""
    return request.param

@pytest.fixture(scope='session')
def techniques(request):
    """Represents each technique dictionary"""
    return request.param

@pytest.fixture(scope='session')
def case_studies(request):
    """Represents each case study dictionary."""
    if hasattr(request, "param"):
        return request.param
    else:
        return pytest.skip("")

@pytest.fixture(scope='session')
def mitigations(request):
    """Represents each mitigation dictionary."""
    if hasattr(request, "param"):
        return request.param
    else:
        return pytest.skip()

@pytest.fixture(scope='session')
def text_with_possible_markdown_syntax(request):
    """Represents the descriptions field of tactics, techniques, and case study procedure steps,
    which can have Markdown links and syntax.
    """
    return request.param

@pytest.fixture(scope='session')
def text_to_be_spellchecked(request):
    """Represents the text fields that can be spellchecked, including:
        - tactic and technique names and descriptions
        - case study names and summaries, procedure step descriptions
    """
    return request.param

@pytest.fixture(scope='session')
def all_data_objects(request):
    """Represents IDs in data objects, such as tactics, techniques, and case studies. """
    return request.param

@pytest.fixture(scope='session')
def unmatched_techniques(request):
    """Represents four-element tuples containing:
        - Case study ID and procedure step number 
        - Technique ID from case study
        - Tactic ID from case study
        - An array containing tactic IDs extracted from technique data from matrices. """
    return request.param

#endregion

def pytest_generate_tests(metafunc):
    """Enables test functions that use the above fixtures to operate on a
    single dictionary, where each test function is automatically run once
    for each dictionary in the tactics/techniques/case studies lists.

    Loads in the ATLAS data and sets up the pytest scheme to yield one
    dictionary for each above fixture, as well as other test fixtures.

    https://docs.pytest.org/en/stable/parametrize.html#basic-pytest-generate-tests-example
    """
    # Read the YAML files in this repository and create the nested dictionary
    path_to_data_file = 'data/data.yaml'
    data = load_atlas_data(path_to_data_file)

    # Parametrize when called for via test signature
    if 'output_data' in metafunc.fixturenames:
        # Only one arg, wrap in list
        metafunc.parametrize('output_data', [data], indirect=True, scope='session')
    if 'matrix' in metafunc.fixturenames:
        metafunc.parametrize('matrix', data['matrices'], indirect=True, scope='session')

    ## Create parameterized fixtures for tactics, techniques, and case studies for schema validation

    # Generated fixtures are for all data objects within matrices, or at the top-level of the data
    fixture_names = []

    # There should always be at least one matrix defined
    matrices = data['matrices']

    # Keys in the data that are metadata and will never be considered keys for data objects
    excluded_keys = ['id', 'name', 'version', 'matrices']

    # Unique keys in each matrix, representing the plural name of the object type
    # Note the underscore instead of the dash
    collect_fixture_names = lambda data: list({key.replace('-','_') for d in data for key in d.keys() if key not in excluded_keys})

    # Construct list of data object keys in the top-level data
    # Wrap this argument in a list to support iteration in lambda function
    data_keys_set = collect_fixture_names([data])
    # As well as unique keys from each matrix
    matrix_keys_set = collect_fixture_names(matrices)
    # Combine these two
    fixture_names = data_keys_set + matrix_keys_set

    # Initialize collections
    text_with_possible_markdown_syntax = []
    text_to_be_spellchecked = []
    all_values = []
    procedure_technique_tactic_ids = []
    technique_to_tactic_dict = {}

    for fixture_name in fixture_names:
        # Handle the key 'case_studies' really being 'case-studies' in the input
        key = fixture_name.replace('_','-')
        # List of tuples that hold the ID and the corresponding object
        # For tactics and techniques
        values = [(obj['id'], obj) for matrix in matrices if key in matrix for obj in matrix[key]]
                    
        # Creates a list of tuples across all fixture names
        all_values.extend(values)
        # For case studies
        if key in data:
            id_to_obj = [(obj['id'], obj) for obj in data[key]]
            all_values.extend(id_to_obj)

        # For unmatched technique test
        technique_to_tactic_dict = {obj['id'] : obj['tactics'] for matrix in matrices if key in matrix for obj in matrix[key] if obj['object-type'] == 'technique' and 'tactics' in obj}

    # Parametrize when called for via test signature
    if 'all_data_objects' in metafunc.fixturenames:
        metafunc.parametrize('all_data_objects', [all_values], indirect=True, scope='session')

    # Parameterize based on data objects
    for fixture_name in fixture_names:

        # Handle the key 'case_studies' really being 'case-studies' in the input
        key = fixture_name.replace('_','-')

        # Construct a list of objects across all matrices under the specified key
        values = [obj for matrix in matrices if key in matrix for obj in matrix[key]]

        # Add top-level objects, if exists, ex. case-studies appended to an empty list from above
        if key in data:
            values.extend(data[key])

        # Build up text parameters
        # Parameter format is (test_identifier, text)
        if key == 'case-studies':

            for cs in values:

                cs_id = cs['id']
                
                text_to_be_spellchecked.append((f"{cs_id} Name", cs['name']))
                text_to_be_spellchecked.append((f"{cs_id} Summary", cs['summary']))

                # AML.CS0000 Procedure #3, <procedure step description>

                procedure_ids = [(f"{cs_id} Procedure Step #{i+1}", step.get('technique'), step.get('tactic'), technique_to_tactic_dict.get(step.get('technique')[0:9])) for i, step in enumerate(cs['procedure'])]
                procedure_technique_tactic_ids.extend(procedure_ids)

                procedure_step_texts = [(f"{cs_id} Procedure #{i+1}", p['description']) for i, p in enumerate(cs['procedure'])]
                text_to_be_spellchecked.extend(procedure_step_texts)
                text_with_possible_markdown_syntax.extend(procedure_step_texts)
        else:
            # This based off of a default ATLAS data object
            for t in values:
                t_id = t['id']
                text_to_be_spellchecked.append((f"{t_id} Name", t['name']))

                description_text = (f"{t_id} Description", t['description'])
                text_to_be_spellchecked.append(description_text)
                text_with_possible_markdown_syntax.append(description_text)

        # Parametrize when called for via test signature
        if fixture_name in metafunc.fixturenames:
            # Parametrize each object, using the ID as identifier
            metafunc.parametrize(fixture_name, values, ids=lambda x: x['id'], indirect=True, scope='session')

    ## Create parameterized fixtures for Markdown link syntax verification - technique descriptions and case study procedure steps

    if 'unmatched_techniques' in metafunc.fixturenames:
        metafunc.parametrize('unmatched_techniques', procedure_technique_tactic_ids, ids=lambda x: x[0], indirect=True, scope='session')

    # Parametrize when called for via test signature
    if 'text_with_possible_markdown_syntax' in metafunc.fixturenames:
        metafunc.parametrize('text_with_possible_markdown_syntax', text_with_possible_markdown_syntax, ids=lambda x: x[0], indirect=True, scope='session')

    ## Create parameterized fixtures for text to be spell-checked - names, descriptions, summary

    # Parametrize when called for via test signature
    if 'text_to_be_spellchecked' in metafunc.fixturenames:
        metafunc.parametrize('text_to_be_spellchecked', text_to_be_spellchecked, ids=lambda x: x[0], indirect=True, scope='session')

#region Schemas
@pytest.fixture(scope='session')
def output_schema():
    """Defines the schema and validation for the ATLAS YAML output data."""
    return atlas_matrix.atlas_output_schema

@pytest.fixture(scope='session')
def matrix_schema():
    """Defines the schema and validation for the ATLAS matrix."""
    return atlas_matrix.atlas_matrix_schema

@pytest.fixture(scope='session')
def tactic_schema():
    """Defines the schema and validation for the tactic object."""
    return atlas_obj.tactic_schema

@pytest.fixture(scope='session')
def technique_schema():
    """Defines the schema and validation for a top-level technique object."""
    return atlas_obj.technique_schema

@pytest.fixture(scope='session')
def subtechnique_schema():
    """Defines the schema and validation for a subtechnique object."""
    return atlas_obj.subtechnique_schema

@pytest.fixture(scope='session')
def case_study_schema():
    """Defines the schema and validation for a case study object."""
    return atlas_obj.case_study_schema

@pytest.fixture(scope='session')
def mitigation_schema():
    """Defines the schema and validation for a mitigation object."""
    return atlas_obj.mitigation_schema
#endregion