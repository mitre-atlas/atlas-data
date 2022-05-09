from schema import Regex, Schema

"""Describes ATLAS ID schemas."""

# Constants for ID parts

# Examples of ID Prefixes include, but are not limited to:
#   ABC. || ABC123. || ABC.XYZ. || ABC.XYZ789.QW3RTY.
ID_PREFIX_PATTERN = (
    r'(?:'          # Start a non-capturing group
        r'[A-Z]+'   # ID must start with uppercase letters
        r'\d*'      # Optionally followed by a set of numbers
        r'\.'       # Then a dot
    r')+'           # There can be one or more of these patterns in a row
)

# Number of digits allowed in the ID portion of a the top-level object and sub-level object
ID_NUM_PATTERN_TOP_LEVEL = r'\d{4}' # i.e. T1234
ID_NUM_PATTERN_SUB_LEVEL = r'\d{3}' # i.e. T0000.123

# Helper methods for ID formats
def create_top_level_object_id(object_prefix):
    """Returns a full ID for a top-level data object.

    Ex. AML.TA0000, where TA is the provided argument
    """
    return (
        rf'{ID_PREFIX_PATTERN}'
        rf'{object_prefix}'
        rf'{ID_NUM_PATTERN_TOP_LEVEL}'
    )

def create_sub_level_object_id(top_level_object_id):
    """Returns a full ID for a sub-level data object.

    Ex. AML.T0000.000, where AML.T0000 is the provided argument
    """
    return (
        rf'{top_level_object_id}'
         r'\.'
        rf'{ID_NUM_PATTERN_SUB_LEVEL}'
    )

# Constants for ID formats
TACTIC_ID_PATTERN       = create_top_level_object_id('TA')                  # AML.TA0000 || AML.ABC123.TA0000 || AML123.TA0000
TECHNIQUE_ID_PATTERN    = create_top_level_object_id('T')                   # AML.T0000 || AML.ABC123.T0000 || AML123.T0000
SUBTECHNIQUE_ID_PATTERN = create_sub_level_object_id(TECHNIQUE_ID_PATTERN)  # AML.T0000.000 || AML.ABC123.T0000.00 || AML123.T0000.00
CASE_STUDY_ID_PATTERN   = create_top_level_object_id('CS')                  # AML.CS0000 || AML.ABC123.CS0000 || AML123.CS0000
MITIGATION_ID_PATTERN   = create_top_level_object_id('M')                   # AML.M0000 || AML.ABC123.M0000 || AML123.M0000

# Exact match patterns for the above, in Schema form
TACTIC_ID_REGEX_EXACT = Schema(
    Regex(rf'^{TACTIC_ID_PATTERN}$'),
    name="id_tactic",
    as_reference=True
)
TECHNIQUE_ID_REGEX_EXACT = Schema(
    Regex(rf'^{TECHNIQUE_ID_PATTERN}$'),
    name="id_technique",
    as_reference=True
)
SUBTECHNIQUE_ID_REGEX_EXACT = Schema(
    Regex(rf'^{SUBTECHNIQUE_ID_PATTERN}$'),
    name="id_subtechnique",
    as_reference=True
)
CASE_STUDY_ID_REGEX_EXACT = Schema(
    Regex(rf'^{CASE_STUDY_ID_PATTERN}$'),
    name="id_case_study",
    as_reference=True
)
MITIGATION_ID_REGEX_EXACT = Schema(
    Regex(rf'^{MITIGATION_ID_PATTERN}$'),
    name="id_mitigation",
    as_reference=True
)
