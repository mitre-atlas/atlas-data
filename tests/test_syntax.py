import re
import warnings

import pytest

from conftest import TACTIC_ID_REGEX, TECHNIQUE_ID_REGEX, SUBTECHNIQUE_ID_REGEX
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
    rf'^/tactics/{TACTIC_ID_REGEX.pattern_str}'
    r'|'
    rf'/techniques/{SUBTECHNIQUE_ID_REGEX.pattern_str}' # Match subtechnique pattern first because top-level technique also matches this
    r'|'
    rf'/techniques/{TECHNIQUE_ID_REGEX.pattern_str}$'
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
        msg = 'Not recognized by spellcheck - fix or exclude in tests/spellcheck.py: '
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

    # Warn on non-ascii for YAML output
    if not text.isascii():
        # Potentially an unicode quote or similar
        msg = f'Contains non-ascii, consider fixing. YAML output will be the literal string: {ascii(text)}'
        warnings.warn(msg)
