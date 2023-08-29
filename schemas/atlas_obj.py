import datetime

from schema import Or, Optional, Schema

from .atlas_id import (
    TACTIC_ID_REGEX_EXACT,
    TECHNIQUE_ID_REGEX_EXACT,
    SUBTECHNIQUE_ID_REGEX_EXACT,
    CASE_STUDY_ID_REGEX_EXACT,
    MITIGATION_ID_REGEX_EXACT
)

"""Describes ATLAS object schemas.

The Schema objects defined are set to be definitions referenced
by the provided name.
"""

references_schema = Schema(
    [
        {
            "title": Or(str, None),
            "url": Or(str, None)
        }
    ],
    name="references",
    as_reference=True
)

tactic_schema = Schema(
    {
        "id": TACTIC_ID_REGEX_EXACT,
        "object-type": 'tactic',
        "description": str,
        "name": str,
        Optional("references"): references_schema
    },
    name="tactic",
    as_reference=True,
    ignore_extra_keys=True
)

technique_schema = Schema(
    {
        "id": TECHNIQUE_ID_REGEX_EXACT,
        "object-type": "technique",
        "name": str,
        "description": str,
        "tactics": [
            TACTIC_ID_REGEX_EXACT # List of tactic IDs
        ],
        Optional("references"): references_schema
    },
    name="technique",
    as_reference=True,
    ignore_extra_keys=True
)

subtechnique_schema = Schema(
    {
        "id": SUBTECHNIQUE_ID_REGEX_EXACT,
        "object-type": "technique",
        "name": str,
        "description": str,
        "subtechnique-of": TECHNIQUE_ID_REGEX_EXACT, # Top-level technique ID
        Optional("references"): references_schema
    },
    name="subtechnique",
    as_reference=True,
    ignore_extra_keys=True
)

CASE_STUDY_VERSION = '1.1'
case_study_schema = Schema(
    {
        "id": CASE_STUDY_ID_REGEX_EXACT,
        "object-type": "case-study",
        "name": str,
        "summary": str,
        "incident-date": datetime.date,
        "incident-date-granularity": Or('YEAR', 'MONTH', 'DATE'),
        "procedure": [
            {
                "tactic": TACTIC_ID_REGEX_EXACT,
                "technique": Or(
                    TECHNIQUE_ID_REGEX_EXACT,   # top-level techniquye
                    SUBTECHNIQUE_ID_REGEX_EXACT # subtechnique
                ),
                "description": str
            }
        ],
        Optional("reporter"): str,
        Optional("target"): str,
        Optional("actor"): str,
        Optional("case-study-type"): Or('incident', 'exercise'),
        Optional("references"): references_schema
    },
    name="case_study",
    as_reference=True
)

mitigation_schema = Schema(
    {
        "id": MITIGATION_ID_REGEX_EXACT,
        "object-type": "mitigation",
        "name": str,
        "description": str,
        Optional("techniques"): [
            Or(
                TECHNIQUE_ID_REGEX_EXACT,   # top-level techniquye
                SUBTECHNIQUE_ID_REGEX_EXACT, # subtechnique
                {   # Specific mitigation for each technique
                    "id": Or (
                        TECHNIQUE_ID_REGEX_EXACT,
                        SUBTECHNIQUE_ID_REGEX_EXACT
                    ),
                    "use": str
                }
            ),
        ],
        Optional("references"): references_schema
    },
    name="mitigation",
    as_reference=True,
    ignore_extra_keys=True
)