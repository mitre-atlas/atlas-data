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
def matrix(request):
    """Represents the ATLAS matrix (ATLAS.yaml) dictionary."""
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
    return request.param

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
    path_to_matrix_file = 'data/matrix.yaml'
    data = load_atlas_data(path_to_matrix_file)

    # Parametrize when called for via test signature
    if 'matrix' in metafunc.fixturenames:
        # Only one arg, wrap in list
        metafunc.parametrize('matrix', [data], indirect=True, scope='session')

    ## Create parameterized fixtures for tactics, techniques, and case studies for schema validation

    # These are the top-level keys of that dictionary
    # and also the names of the fixtures we'd like to generate.
    # Note the underscore instead of the dash
    keys = ['tactics', 'techniques', 'case_studies']

    for key in keys:
        # Parametrize when called for via test signature
        if key in metafunc.fixturenames:
            # Handle the key 'case_studies' really being 'case-studies' in the input
            values = data[key.replace('_','-')]
            # Parametrize each object, using the ID as identifier
            metafunc.parametrize(key, values, ids=lambda x: x['id'], indirect=True, scope='session')

    ## Create parameterized fixtures for Markdown link syntax verification - technique descriptions and case study procedure steps

    # Parameter format is (test_identifier, text)
    text_with_possible_markdown_syntax = [(f"{t['id']} Description", t['description']) for t in data['techniques']]
    for cs in data['case-studies']:
        # Identify in test with case study ID + P#{1-based index of procedure step}
        text_with_possible_markdown_syntax.extend([(f"{cs['id']} Procedure #{i+1}", p['description']) for i, p in enumerate(cs['procedure'])])
    # Parametrize when called for via test signature
    if 'text_with_possible_markdown_syntax' in metafunc.fixturenames:
        metafunc.parametrize('text_with_possible_markdown_syntax', text_with_possible_markdown_syntax, ids=lambda x: x[0], indirect=True, scope='session')

    ## Create parameterized fixtures for text to be spell-checked - names, descriptions, summary
    # Parameter format is (text_identifier, text)

    # Start with existing descriptions from technique descriptions and case study procedure steps
    text_to_be_spellchecked = text_with_possible_markdown_syntax
    # Tactic text
    for t in data['tactics']:
        text_to_be_spellchecked.append((f"{t['id']} Name", t['name']))
        text_to_be_spellchecked.append((f"{t['id']} Description", t['description']))
    # Already contains technique descriptions, add names
    text_to_be_spellchecked.extend([(f"{t['id']} Name", t['name']) for t in data['techniques']])
    # Case study text
    for cs in data['case-studies']:
        text_to_be_spellchecked.append((f"{cs['id']} Name", cs['name']))
        text_to_be_spellchecked.append((f"{cs['id']} Summary", cs['summary']))

    # Parametrize when called for via test signature
    if 'text_to_be_spellchecked' in metafunc.fixturenames:
        metafunc.parametrize('text_to_be_spellchecked', text_to_be_spellchecked, ids=lambda x: x[0], indirect=True, scope='session')


#region Schemas
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
#endregion