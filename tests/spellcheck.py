import os
from spellchecker import SpellChecker

"""
Sets up usage of https://pyspellchecker.readthedocs.io/en/latest/.
"""

# Add words to the spellcheck by adding to this file
custom_words_file = os.path.join(os.path.dirname(__file__), "custom_words.txt")

# Read in list of words
with open(custom_words_file) as f:
    CUSTOM_WORDS = [w.strip() for w in f.readlines()]

# Create English spell checker with additional custom words for syntax test use
SPELL_CHECKER = SpellChecker()
SPELL_CHECKER.word_frequency.load_words(CUSTOM_WORDS)
