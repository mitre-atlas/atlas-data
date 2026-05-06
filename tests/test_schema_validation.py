import pytest
from schema import SchemaError, SchemaWrongKeyError

"""
Validates ATLAS data objects against schemas defined in conftest.py.
"""

def test_validate_output_data(output_schema, output_data):
    """Validates the ATLAS data output dictionary.
    Explicitly fails with message to capture more in pytest short test info.
    """
    try:
        output_schema.validate(output_data)
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
    """Handles subtechniques by attempting top-level validation first, then
    falling back to the subtechnique schema when specific key/format errors
    are encountered.
    """
    try:
        # Check if dictionary is a top-level technique
        technique_schema.validate(techniques)
    except (SchemaWrongKeyError, SchemaError) as e:
        # Could be a subtechnique
        #   SchemaWrongKeyError: flagging on presence of 'subtechnique-of'
        #   SchemaError: flagging on ID having extra numbers at end
        #   Failed: 'technique' Missing key: 'tactics'
        if e.code.startswith("Wrong key 'subtechnique-of'") or "does not match" in e.code or 'Missing key: \'tactics\'' in e.code:
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

import datetime


def make_tactic(id="AML.TA0001", name="Example Tactic", description="Tactic description", include_id=True):
    obj = {
        "object-type": "tactic",
        "name": name,
        "description": description,
    }
    if include_id:
        obj["id"] = id
    return obj


def make_technique(
    id="AML.T0002",
    name="Example Technique",
    description="Technique description",
    tactics=None,
    maturity=None,
    include_id=True,
    include_tactics=True,
):
    if tactics is None:
        tactics = ["AML.TA0001"]
    obj = {
        "object-type": "technique",
        "name": name,
        "description": description,
    }
    if include_id:
        obj["id"] = id
    if include_tactics:
        obj["tactics"] = tactics
    if maturity is not None:
        obj["maturity"] = maturity
    return obj


def make_mitigation(id="AML.M0003", name="Example Mitigation", description="Mitigation description", include_id=True):
    obj = {
        "object-type": "mitigation",
        "name": name,
        "description": description,
    }
    if include_id:
        obj["id"] = id
    return obj


def make_case_study(
    id="AML.CS0004",
    name="Example Case Study",
    summary="Case study summary",
    incident_date=datetime.date(2024, 1, 1),
    incident_granularity="DATE",
    include_id=True,
    include_object_type=True,
):
    obj = {
        "name": name,
        "summary": summary,
        "incident-date": incident_date,
        "incident-date-granularity": incident_granularity,
        "procedure": [
            {
                "tactic": "AML.TA0001",
                "technique": "AML.T0002",
                "description": "Procedure step description",
            }
        ],
    }
    if include_id:
        obj["id"] = id
    if include_object_type:
        obj["object-type"] = "case-study"
    return obj


def make_website_case_study(**kwargs):
    return {
        "study": make_case_study(**kwargs),
    }


def make_other(description="Free-form contribution"):
    return {
        "object-type": "other",
        "description": description,
    }


def make_subtechnique(
    id="AML.T0002.001",
    name="Example Subtechnique",
    description="Subtechnique description",
    parent_technique="AML.T0002",
):
    return {
        "id": id,
        "object-type": "technique",
        "name": name,
        "description": description,
        "subtechnique-of": parent_technique,
    }


def test_contributions_minimal(contributions_schema):
    payload = {
        "contact": {"name": "Alice", "emails": "alice@example.com"},
        "additional-info": "Additional details",
        "submissions": [make_tactic()],
    }
    try:
        contributions_schema.validate(payload)
    except SchemaError as e:
        pytest.fail(e.code)


def test_contributions_mixed_valid(contributions_schema):
    payload = {
        "contact": {"name": "Alice", "emails": "alice@example.com"},
        "additional-info": "Batch submissions",
        "submissions": [
            make_tactic(),
            make_technique(),
            make_mitigation(),
            make_website_case_study(),
            make_other(),
        ],
    }
    try:
        contributions_schema.validate(payload)
    except SchemaError as e:
        pytest.fail(e.code)


def test_contact_allows_none(contributions_schema):
    payload = {
        "contact": {"name": None, "emails": None},
        "additional-info": "Info",
        "submissions": [make_tactic()],
    }
    try:
        contributions_schema.validate(payload)
    except SchemaError as e:
        pytest.fail(e.code)


def test_technique_maturity_valid(contributions_schema):
    for v in ["feasible", "demonstrated", "realized"]:
        payload = {
            "contact": {"name": "Bob", "emails": "bob@example.com"},
            "additional-info": "Info",
            "submissions": [make_technique(maturity=v)],
        }
        try:
            contributions_schema.validate(payload)
        except SchemaError as e:
            pytest.fail(e.code)


def test_technique_maturity_invalid(contributions_schema):
    payload = {
        "contact": {"name": "Bob", "emails": "bob@example.com"},
        "additional-info": "Info",
        "submissions": [make_technique(maturity="experimental")],
    }
    with pytest.raises(SchemaError):
        contributions_schema.validate(payload)


def test_extra_keys_tactic_technique_allowed(contributions_schema):
    tactic = make_tactic()
    tactic["extra-key"] = "x"
    tech = make_technique()
    tech["extra-key"] = "y"
    payload = {
        "contact": {"name": "Carol", "emails": "carol@example.com"},
        "additional-info": "Info",
        "submissions": [tactic, tech],
    }
    try:
        contributions_schema.validate(payload)
    except SchemaError as e:
        pytest.fail(e.code)


def test_case_study_rejects_extra_keys(contributions_schema):
    cs = make_website_case_study()
    cs["study"]["unexpected"] = "value"
    payload = {
        "contact": {"name": "Carol", "emails": "carol@example.com"},
        "additional-info": "Info",
        "submissions": [cs],
    }
    with pytest.raises((SchemaWrongKeyError, SchemaError)):
        contributions_schema.validate(payload)


def test_submissions_rejects_subtechnique(contributions_schema):
    payload = {
        "contact": {"name": "Dave", "emails": "dave@example.com"},
        "additional-info": "Info",
        "submissions": [make_subtechnique()],
    }
    with pytest.raises(SchemaError):
        contributions_schema.validate(payload)


def test_invalid_submission_object_shape(contributions_schema):
    bad_tactic = {"object-type": "tactic"}
    payload = {
        "contact": {"name": "Eve", "emails": "eve@example.com"},
        "additional-info": "Info",
        "submissions": [bad_tactic],
    }
    with pytest.raises(SchemaError):
        contributions_schema.validate(payload)


def test_missing_top_level_keys_contact(contributions_schema):
    payload = {
        "additional-info": "Info",
        "submissions": [make_tactic()],
    }
    with pytest.raises(SchemaError):
        contributions_schema.validate(payload)


def test_missing_top_level_keys_additional_info(contributions_schema):
    payload = {
        "contact": {"name": "Frank", "emails": "frank@example.com"},
        "submissions": [make_tactic()],
    }
    with pytest.raises(SchemaError):
        contributions_schema.validate(payload)


def test_submissions_invalid_type(contributions_schema):
    payload = {
        "contact": {"name": "Gina", "emails": "gina@example.com"},
        "additional-info": "Info",
        "submissions": {"not": "a list"},
    }
    with pytest.raises(SchemaError):
        contributions_schema.validate(payload)


def test_submissions_empty_list_allowed(contributions_schema):
    payload = {
        "contact": {"name": "Hank", "emails": "hank@example.com"},
        "additional-info": "Info",
        "submissions": [],
    }
    try:
        contributions_schema.validate(payload)
    except SchemaError as e:
        pytest.fail(e.code)


def test_contact_invalid_shape(contributions_schema):
    payload = {
        "contact": {"name": 123, "emails": ["x@example.com"]},
        "additional-info": "Info",
        "submissions": [make_tactic()],
    }
    with pytest.raises(SchemaError):
        contributions_schema.validate(payload)


def test_case_study_incident_date_invalid(contributions_schema):
    cs = make_website_case_study()
    cs["study"]["incident-date"] = "2024-01-01"
    payload = {
        "contact": {"name": "Ivy", "emails": "ivy@example.com"},
        "additional-info": "Info",
        "submissions": [cs],
    }
    with pytest.raises(SchemaError):
        contributions_schema.validate(payload)


def test_contributions_allow_website_relaxations(contributions_schema):
    payload = {
        "contact": {"name": "Jules", "emails": "jules@example.com"},
        "additional-info": "New website-generated submissions",
        "submissions": [
            make_tactic(include_id=False),
            make_technique(include_id=False, include_tactics=False),
            make_mitigation(include_id=False),
            make_website_case_study(include_id=False, include_object_type=False),
        ],
    }
    try:
        contributions_schema.validate(payload)
    except SchemaError as e:
        pytest.fail(e.code)


def test_contributions_allow_valid_matrix_associations(contributions_schema):
    tactic = make_tactic(include_id=False)
    tactic["techniques"] = [
        "AML.T0002",
        make_technique(include_id=False, include_tactics=False),
    ]

    technique = make_technique(include_id=False)
    technique["tactics"] = [
        "AML.TA0001",
        make_tactic(include_id=False),
    ]
    technique["mitigations"] = [
        "AML.M0003",
        make_mitigation(include_id=False),
    ]

    mitigation = make_mitigation(include_id=False)
    mitigation["techniques"] = [
        {"id": "AML.T0002", "use": "How the mitigation applies to this technique"},
        {
            **make_technique(include_id=False, include_tactics=False),
            "use": "How the mitigation applies to this new technique",
        },
    ]
    mitigation["mitigation-category"] = "Preventative"
    mitigation["ml-lifecycle"] = ["Model Development"]

    payload = {
        "contact": {"name": "Jules", "emails": "jules@example.com"},
        "additional-info": "New website-generated submissions",
        "submissions": [tactic, technique, mitigation],
    }
    try:
        contributions_schema.validate(payload)
    except SchemaError as e:
        pytest.fail(e.code)


def test_contributions_reject_mitigation_technique_association_without_use(contributions_schema):
    invalid_associations = [
        "AML.T0002",
        {"id": "AML.T0002"},
        make_technique(include_id=False, include_tactics=False),
    ]

    for association in invalid_associations:
        mitigation = make_mitigation(include_id=False)
        mitigation["techniques"] = [association]
        payload = {
            "contact": {"name": "Jules", "emails": "jules@example.com"},
            "additional-info": "New website-generated submissions",
            "submissions": [mitigation],
        }

        with pytest.raises(SchemaError):
            contributions_schema.validate(payload)


def test_contributions_reject_invalid_matrix_associations(contributions_schema):
    invalid_tactic = make_tactic(include_id=False)
    invalid_tactic["mitigations"] = ["AML.M0003"]

    invalid_technique = make_technique(include_id=False)
    invalid_technique["techniques"] = ["AML.T0002"]

    invalid_mitigation = make_mitigation(include_id=False)
    invalid_mitigation["tactics"] = ["AML.TA0001"]

    for submission in [invalid_tactic, invalid_technique, invalid_mitigation]:
        payload = {
            "contact": {"name": "Jules", "emails": "jules@example.com"},
            "additional-info": "New website-generated submissions",
            "submissions": [submission],
        }
        with pytest.raises(SchemaError):
            contributions_schema.validate(payload)


def test_contributions_allow_inline_new_procedure_ttm(contributions_schema):
    cs = make_website_case_study(include_id=False, include_object_type=False)
    cs["study"]["procedure"] = [
        {
            "tactic": make_tactic(include_id=False),
            "technique": make_technique(include_id=False, include_tactics=False),
            "description": "Procedure step using newly submitted tactic and technique",
        }
    ]
    payload = {
        "contact": {"name": "Jules", "emails": "jules@example.com"},
        "additional-info": "New website-generated submissions",
        "submissions": [cs],
    }
    try:
        contributions_schema.validate(payload)
    except SchemaError as e:
        pytest.fail(e.code)


def test_contributions_reject_raw_case_study_submission(contributions_schema):
    payload = {
        "contact": {"name": "Kai", "emails": "kai@example.com"},
        "additional-info": "Info",
        "submissions": [make_case_study()],
    }
    with pytest.raises(SchemaError):
        contributions_schema.validate(payload)
