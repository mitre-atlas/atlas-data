from schema import Regex, Schema

"""Describes ATLAS ID schemas."""

# Constants for ID formats
TACTIC_ID_PATTERN       = r'AML\.TA\d{4}'         # AML.TA0000
TECHNIQUE_ID_PATTERN    = r'AML\.T\d{4}'          # AML.T0000
SUBTECHNIQUE_ID_PATTERN = r'AML\.T\d{4}\.\d{3}'   # AML.T0000.000
CASE_STUDY_ID_PATTERN   = r'AML\.CS\d{4}'         # AML.CS0000

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
