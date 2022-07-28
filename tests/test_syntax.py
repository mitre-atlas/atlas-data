import re
import warnings

import pytest

from schemas.atlas_id import TACTIC_ID_PATTERN, TECHNIQUE_ID_PATTERN, SUBTECHNIQUE_ID_PATTERN
from spellcheck import SPELL_CHECKER

"""
Validates text for internal and external Markdown links and warns for spelling.
"""

# Markdown Link syntax
# [title](url)
REGEX_MARKDOWN_LINK = re.compile(r'\[([^\[]+)\]\((.*?)\)')

# Fully-qualified URLs
# https://stackoverflow.com/a/17773849
REGEX_URL = re.compile(r'^(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})$')

# Internal Markdown links, assumed to be only to /tactics/ and /techniques/
# Note that the regex objects here are from conftest.py and are the schema library's objects, hence the pattern_str property
REGEX_INTERNAL_URL = re.compile(
    rf'^/tactics/{TACTIC_ID_PATTERN}'
    r'|'
    rf'/techniques/{SUBTECHNIQUE_ID_PATTERN}' # Match subtechnique pattern first because top-level technique also matches this
    r'|'
    rf'/techniques/{TECHNIQUE_ID_PATTERN}$'
    )

def test_markdown_link(text_with_possible_markdown_syntax):
    """Validates Markdown link syntax for internal and external links.

    Assumes that external links are fully qualified, i.e. start with http(s) and other URL constraints.
    Assumes that internal links are to /tactics/ and /techniques/ and match ID formats.
    """
    # Text is second element in tuple of (text identifier, text)
    text = text_with_possible_markdown_syntax[1]
    # Find all Markdown links fitting the []() syntax
    links = REGEX_MARKDOWN_LINK.findall(text)
    # Track error messages
    errors = []

    # Iterate over parts of Markdown link
    for title, url in links:
        # Title
        if not title:
            # Titles should not be empty
            errors.append(f'Got empty title for Markdown link with URL ({url})')

        elif '{' in title:
            # Titles shouldn't contain curly brackets like in a dict (ex. if anchor typo of "anchor" instead of "anchor.name")
            errors.append(f'Expected not to find the character {{ in Markdown link title, got {title}')

        # URL
        if not url:
            # URLs should not be empty
            errors.append(f'Got empty URL for Markdown link with title [{title}]')

        elif url.startswith('http') and REGEX_URL.match(url) is None:
            # Ensure that external URL is fully-qualified and doesn't contain invalid characters
            errors.append(f'Expected a fully-qualified URL, got ({url})')

        elif not url.startswith('http'):
            # Internal ATLAS link should match expected prefix and ID syntax
            if not REGEX_INTERNAL_URL.match(url):
                errors.append(f'Expected internal Markdown link URL to start with /techniques/ or /tactics/ and match ID format, got ({url})')

    if errors:
        # Fail test with error messages
        error_str = '\n'.join(errors)
        pytest.fail(error_str)


# Parses out string tokens to be spell checked
REGEX_WORDS = re.compile(
    r"\b"           # Start at word boundary
        r"(?!s)"            # Excludes just "s", i.e. from a posessive
        r"(?![iegUS]\.)"    # Excludes i.e., e.g., U.S.
        r"(?!\d+[MKB]\b)"   # Excludes 70K, M, B
    r"(?:"          # Non capture group
        r"[\w&]+"       # All words, can have &, i.e. R&D
        r"(?:'t)?"      # Optionally include contractions
        r"(?:\(s\))?"   # Optionally include (s) at end
    r")"
    )

def test_spelling(text_to_be_spellchecked):
    """Warns for potentially mispelled words from names and descriptions.
    Only checks text outside of Markdown links.
    See tests/custom_words.txt for exclusion words.
    """
    # Text is second element in tuple of (text identifier, text)
    text = text_to_be_spellchecked[1]
    # Remove Markdown links
    stripped_text = REGEX_MARKDOWN_LINK.sub('', text)
    # Tokenize, see comments above at variable declaration
    text_tokens = REGEX_WORDS.findall(stripped_text)

    # Get a set of potentially mispelled words
    possible_mispelled = SPELL_CHECKER.unknown(text_tokens)
    if possible_mispelled:
        # Emit warnings
        msg = 'Not recognized by spellcheck - fix or exclude in tests/custom_words.txt: '
        warnings.warn(msg + str(possible_mispelled))

def test_ascii(text_to_be_spellchecked):
    """Warns for text containing non-ascii characters, likely from copy and pastes,
    which will cause YAML output to be a literal YAML string and reduce readability.

    Example:
        ’, the unicode right single quotation mark is rendered as \u2019 in a literal string,
        along with explicit newline characters \n.
        Replacing with ' produces a regular YAML string.
    """
    # Text is second element in tuple of (text identifier, text)
    text = text_to_be_spellchecked[1]
    do_warn = False
    try:
        # Check for non-ascii text in Python 3.7+
        if not text.isascii():
            do_warn = True
    except AttributeError:
        # Fallback for older versions of Python
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            do_warn = True

    # Warn on non-ascii for YAML output
    if do_warn:
        # Potentially an unicode quote or similar
        msg = f'Contains non-ascii, consider fixing. YAML output will be the literal string: {ascii(text)}'
        warnings.warn(msg)

def test_check_unique_ids(all_data_objects):
    """ Warns for duplicate IDs in tactics, techniques, case studies, etc. """
    # Creates a list of IDs from all_data_objects, which may contain duplicates
    all_ids = [ids[0] for ids in all_data_objects]

    # Creates a list of 3-element tuples that hold the duplicate IDs, name, and object type
    # Sorted is needed to print the IDs in order
    list_of_duplicate_objects = sorted([(ids[0], ids[1]['name'], ids[1]['object-type']) for ids in all_data_objects if all_ids.count(ids[0]) > 1])
    list_of_duplicate_ids = sorted(set([id[0] for id in list_of_duplicate_objects]))
    
    if len(list_of_duplicate_objects) > 0:

        # Variables needed to turn number of duplicates into string to use in error msg
        num_of_duplicates_as_str = str(len(list_of_duplicate_ids))
        total_num_of_duplicates_as_str = str(len(list_of_duplicate_objects))

        # Main error message
        error_msg = F"Duplicate ID(s) detected: {num_of_duplicates_as_str} ID(s) found for {total_num_of_duplicates_as_str} data objects."
        
        # Adds duplicate ID info (ID, name, object type)
        for dup_id in range(len(list_of_duplicate_ids)):
            tactic_name = [obj[2] for obj in list_of_duplicate_objects if obj[0] == list_of_duplicate_ids[dup_id]]
            error_msg += F"\n\t  {list_of_duplicate_ids[dup_id]}: {tactic_name[0].capitalize()}"
            for dup_object in list_of_duplicate_objects:
                if dup_object[0] == list_of_duplicate_ids[dup_id]:
                    error_msg += F"\n\t\t {dup_object[1]}"
        
        pytest.fail(error_msg)

def check_matching_tactic_subtechnique(all_data_objects):
    # maps techniques to list of tactics
    technique_to_tactic_dict = {technique_obj['id']: [technique_obj['tactics']] for technique_obj in all_data_objects['matrices']['techniques'] if all_data_objects['matrices']['techiques'].keys().contains('tactics')}
    
    unmatched_techniques = []
    # obj is a dictionary
    for obj in all_data_objects[1]:
        if obj['object-type'] == 'case-study':
            for step in obj['procedure']:
                tactic_id = obj['procedure'][step]['tactic']
                technique_id = obj['procedure'][step]['technique'][0:9]
                if not(technique_to_tactic_dict[technique_id].contains(tactic_id)):
                    unmatched_techniques.append((obj['id'], technique_id, tactic_id))
                                
    if len(unmatched_techniques) > 0:

        num_of_unmatched_techniques_as_str = str(len(unmatched_techniques))
        # Main error message
        error_msg = F"{num_of_unmatched_techniques_as_str} unmatched technique(s) in case studies detected."
        for unmatched_obj in unmatched_techniques:
            error_msg += F"\n\t\t The procedure of case study {unmatched_obj[0]} has an unmatched technique: technique {unmatched_obj[1]} is not associated with tactic {unmatched_obj[2]}"
        
        pytest.fail(error_msg)

#                     for obj in all_data_objects[1]:
#                         if obj['object-type'] == 'techniques':
#                             obj[]

# [(obj['case-study']['id'], obj['case-study']['procedure']['tactic'], obj['case-study']['procedure']['technique']) for obj in all_data_objects[1] if obj['object-type']=='case-study' for keys in obj['case-study'] if keys == 'procedure' for step in obj['case-study']['procedure'] if not(step.keys().contains('subtechnique-of'))]


