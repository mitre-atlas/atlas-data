from schema import Optional, Or, Schema

from .atlas_obj import (
    case_study_schema,
    references_schema,
    tactic_schema,
    technique_schema,
)
from .atlas_id import (
    TACTIC_ID_REGEX_EXACT,
    TECHNIQUE_ID_REGEX_EXACT,
    SUBTECHNIQUE_ID_REGEX_EXACT,
    MITIGATION_ID_REGEX_EXACT,
)

WEBSITE_SUBMISSION_VERSION = "1.0.0"

TECHNIQUE_OR_SUBTECHNIQUE_ID = Or(
    TECHNIQUE_ID_REGEX_EXACT,
    SUBTECHNIQUE_ID_REGEX_EXACT,
)

items_to_remove_schema = Schema(
    {
        Optional("tactics"): [TACTIC_ID_REGEX_EXACT],
        Optional("techniques"): [TECHNIQUE_OR_SUBTECHNIQUE_ID],
        Optional("mitigations"): [MITIGATION_ID_REGEX_EXACT],
    },
    name="items_to_remove",
    as_reference=True,
)

def inline_matrix_schema(object_type, name):
    return Schema(
        {
            "object-type": object_type,
            "name": str,
            "description": str,
            Optional("references"): references_schema,
        },
        name=name,
        as_reference=True,
    )


inline_tactic_schema = inline_matrix_schema("tactic", "inline_tactic")
inline_technique_schema = inline_matrix_schema("technique", "inline_technique")
inline_mitigation_schema = inline_matrix_schema("mitigation", "inline_mitigation")
inline_mitigation_technique_schema = Schema(
    {
        **dict(inline_technique_schema.schema),
        "use": str,
    },
    name="inline_mitigation_technique",
    as_reference=True,
)
mitigation_technique_use_schema = Schema(
    {
        "id": TECHNIQUE_OR_SUBTECHNIQUE_ID,
        "use": str,
    },
    name="mitigation_technique_use",
    as_reference=True,
)

TACTIC_ASSOCIATION = Or(TACTIC_ID_REGEX_EXACT, inline_tactic_schema)
TECHNIQUE_ASSOCIATION = Or(
    TECHNIQUE_ID_REGEX_EXACT,
    SUBTECHNIQUE_ID_REGEX_EXACT,
    inline_technique_schema,
)
MITIGATION_ASSOCIATION = Or(MITIGATION_ID_REGEX_EXACT, inline_mitigation_schema)
MITIGATION_TECHNIQUE_ASSOCIATION = Or(
    mitigation_technique_use_schema,
    inline_mitigation_technique_schema,
)


def schema_with_optional_keys(
    schema_obj,
    keys,
    *,
    name,
    as_reference=False,
    ignore_extra_keys=False,
    overrides=None,
):
    """Clone a Schema object and relax selected required keys for website submissions."""

    cloned_schema = dict(schema_obj.schema)
    for key in keys:
        if key in cloned_schema:
            cloned_schema[Optional(key)] = cloned_schema.pop(key)

    if overrides:
        cloned_schema.update(overrides)

    return Schema(
        cloned_schema,
        name=name,
        as_reference=as_reference,
        ignore_extra_keys=ignore_extra_keys,
    )


website_case_study_tactic_schema = schema_with_optional_keys(
    tactic_schema,
    ["id"],
    name="case_study_tactic",
    as_reference=True,
    ignore_extra_keys=True,
)

website_case_study_technique_schema = schema_with_optional_keys(
    technique_schema,
    ["id", "tactics"],
    name="case_study_technique",
    as_reference=True,
    ignore_extra_keys=True,
)

website_tactic_schema = Schema(
    {
        Optional("id"): TACTIC_ID_REGEX_EXACT,
        "object-type": "tactic",
        "description": str,
        "name": str,
        Optional("references"): references_schema,
        Optional("techniques"): [TECHNIQUE_ASSOCIATION],
        Optional("items-to-remove"): items_to_remove_schema,
    },
    name="tactic",
    as_reference=True,
)

website_technique_schema = Schema(
    {
        Optional("id"): TECHNIQUE_ID_REGEX_EXACT,
        "object-type": "technique",
        "name": str,
        "description": str,
        Optional("tactics"): [TACTIC_ASSOCIATION],
        Optional("references"): references_schema,
        Optional("maturity"): Or("feasible", "demonstrated", "realized"),
        Optional("mitigations"): [MITIGATION_ASSOCIATION],
        Optional("items-to-remove"): items_to_remove_schema,
    },
    name="technique",
    as_reference=True,
)

website_mitigation_schema = Schema(
    {
        Optional("id"): MITIGATION_ID_REGEX_EXACT,
        "object-type": "mitigation",
        "name": str,
        "description": str,
        Optional("techniques"): [MITIGATION_TECHNIQUE_ASSOCIATION],
        Optional("references"): references_schema,
        Optional("mitigation-category"): str,
        Optional("ml-lifecycle"): [str],
        Optional("items-to-remove"): items_to_remove_schema,
    },
    name="mitigation",
    as_reference=True,
)

website_case_study_procedure_schema = [
    {
        "tactic": Or(
            TACTIC_ID_REGEX_EXACT,
            website_case_study_tactic_schema,
        ),
        "technique": Or(
            TECHNIQUE_ID_REGEX_EXACT,
            SUBTECHNIQUE_ID_REGEX_EXACT,
            website_case_study_technique_schema,
        ),
        "description": str,
    }
]

website_case_study_schema = schema_with_optional_keys(
    case_study_schema,
    ["id", "object-type"],
    name="website_case_study",
    overrides={"procedure": website_case_study_procedure_schema},
)


def create_website_case_study_wrapper_schema(*, name, as_reference=False):
    return Schema(
        {
            "study": website_case_study_schema,
            Optional("meta"): {
                str: object,
            },
        },
        name=name,
        as_reference=as_reference,
        ignore_extra_keys=True,
    )


# Wrap the current case study object to support website-generated contribution files.
website_case_study_wrapper_schema = create_website_case_study_wrapper_schema(
    name="atlas_website_case_study_schema",
)

website_case_study_submission_schema = create_website_case_study_wrapper_schema(
    name="case_study",
    as_reference=True,
)

# Other contributions
# basically comments, but assigning a type to avoid branching the full schema
other_schema = Schema(
    {
        "object-type": "other",
        "description": str,
    },
    name="other",
    as_reference=True,
    ignore_extra_keys=True,
)


# contact details
contact_schema = Schema(
    {
        "name": Or(str, None),
        "emails": Or(str, None),
    },
    name="contact",
    as_reference=True,
)

# Unified contributions schema
contributions_schema = Schema(
    {
        "contact": contact_schema,
        # free text comments
        "additional-info": str,
        "submissions": [
            Or(
                website_tactic_schema,
                website_technique_schema,
                website_mitigation_schema,
                website_case_study_submission_schema,
                other_schema,
            )
        ],
    },
    name="ATLAS Contribution Schema",
    ignore_extra_keys=True,
)
