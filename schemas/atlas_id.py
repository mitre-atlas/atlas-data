from schema import Regex, Schema

"""Describes ATLAS ID schemas."""

# Constants for ID formats
ID_PREFIX_PATTERN       = r'\w{1,}|\d{1,}(\.\w{1,}|\d{1,})?\.'
TACTIC_ID_PATTERN       = rf'{ID_PREFIX_PATTERN}TA\d{4}'         # AML.TA0000 || AML.ABC123.TA0000 || AML123.TA0000
TECHNIQUE_ID_PATTERN    = rf'{ID_PREFIX_PATTERN}T\d{4}'          # AML.T0000 || AML.ABC123.T0000 || AML123.T0000
SUBTECHNIQUE_ID_PATTERN = rf'{TECHNIQUE_ID_PATTERN}\.\d{3}'      # AML.T0000.000 || AML.ABC123.T0000.00 || AML123.T0000.00
CASE_STUDY_ID_PATTERN   = rf'{ID_PREFIX_PATTERN}CS\d{4}'         # AML.CS0000 || AML.ABC123.CS0000 || AML123.CS0000
MITIGATION_ID_PATTERN   = rf'{ID_PREFIX_PATTERN}M\d{4}'          # AML.M0000 || AML.ABC123.M0000 || AML123.M0000

# Exact match patterns for the above, in Schema form
TACTIC_ID_REGEX_EXACT = Schema(
    Regex(f'^{TACTIC_ID_PATTERN}$'),
    name="id_tactic",
    as_reference=True
)
TECHNIQUE_ID_REGEX_EXACT = Schema(
    Regex(f'^{TECHNIQUE_ID_PATTERN}$'),
    name="id_technique",
    as_reference=True
)
SUBTECHNIQUE_ID_REGEX_EXACT = Schema(
    Regex(f'^{SUBTECHNIQUE_ID_PATTERN}$'),
    name="id_subtechnique",
    as_reference=True
)
CASE_STUDY_ID_REGEX_EXACT = Schema(
    Regex(f'^{CASE_STUDY_ID_PATTERN}$'),
    name="id_case_study",
    as_reference=True
)
MITIGATION_ID_REGEX_EXACT = Schema(
    Regex(f'^{MITIGATION_ID_PATTERN}$'),
    name="id_mitigation",
    as_reference=True
)
