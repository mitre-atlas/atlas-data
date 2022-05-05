import pytest
from schema import SchemaError, SchemaWrongKeyError

"""
Validates ATLAS data objects against schemas defined in conftest.py.
"""

def test_validate_output_data(output_data_schema, output_data):
    """Validates the ATLAS data output dictionary.
    Explicitly fails with message to capture more in pytest short test info.
    """
    try:
        output_data_schema.validate(output_data)
    except SchemaError as e:
        pytest.fail(e.code)

def test_validate_matrix(matrix_schema, matrix):
    """Validates the ATLAS matrix dictionary.
    Explicitly fails with message to capture more in pytest short test info.
    """
    try:
        matrix_schema.validate(matrix)
    except SchemaError as e:
        pytest.fail(e.code)

def test_validate_tactics(tactic_schema, tactics):
    """Validates each tactic dictionary.
    Explicitly fails with message to capture more in pytest short test info.
    """
    try:
        tactic_schema.validate(tactics)
    except SchemaError as e:
        pytest.fail(e.code)

def test_validate_techniques(technique_schema, subtechnique_schema, techniques):
    """Validates each technique dictionary, both top-level and subtechniques.
    Explicitly fails with message to capture more in pytest short test info.
    """
    try:
        # Check if dictionary is a top-level technique
        technique_schema.validate(techniques)
    except (SchemaWrongKeyError, SchemaError) as e:
        # Could be a subtechnique
        #   SchemaWrongKeyError: flagging on presence of 'subtechnique-of'
        #   SchemaError: flagging on ID having extra numbers at end
        if e.code.startswith("Wrong key 'subtechnique-of'") or "does not match" in e.code:
            try:
                # Validate the subtechnique
                subtechnique_schema.validate(techniques)
            except SchemaError as se:
                # Fail with any errors
                pytest.fail(se.code)
        else:
            # Otherwise is another key error
            pytest.fail(e.code)

def test_validate_case_studies(case_study_schema, case_studies):
    """Validates each case study dictionary.
    Explicitly fails with message to capture more in pytest short test info.
    """
    try:
        case_study_schema.validate(case_studies)
    except SchemaError as e:
        pytest.fail(e.code)

def test_validate_mitigations(mitigation_schema, mitigations):
    """Validates each mitigations dictionary.
    Explicitly fails with message to capture more in pytest short test info.
    """
    try:
        mitigation_schema.validate(mitigations)
    except SchemaError as e:
        pytest.fail(e.code)