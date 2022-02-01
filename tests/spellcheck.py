import os
from spellchecker import SpellChecker

"""
Sets up usage of https://pyspellchecker.readthedocs.io/en/latest/.
"""

# Add words to the spellcheck by adding to this list
# Ensure that trailing commas exist, since not having them is valid!
# https://docs.python.org/3/reference/lexical_analysis.html#string-literal-concatenation
# TODO Load in text file https://github.com/barrust/pyspellchecker/blob/master/spellchecker/spellchecker.py#L484

custom_words_file = os.path.join(os.path.dirname(__file__), "custom_words.txt")
with open(custom_words_file) as f:
    CUSTOM_WORDS = [w.strip() for w in f.readlines()]
SPELL_CHECKER = SpellChecker()
SPELL_CHECKER.word_frequency.load_words(CUSTOM_WORDS)
