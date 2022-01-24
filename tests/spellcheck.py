from spellchecker import SpellChecker

"""
Sets up usage of https://pyspellchecker.readthedocs.io/en/latest/.
"""

# Add words to the spellcheck by adding to this list
# Ensure that trailing commas exist, since not having them is valid!
# https://docs.python.org/3/reference/lexical_analysis.html#string-literal-concatenation
# TODO Load in text file https://github.com/barrust/pyspellchecker/blob/master/spellchecker/spellchecker.py#L484
CUSTOM_WORDS = [
  # Technical terms
  "ml", "mlaas", "gpu", "gpus", "classifiers", "apis",
  "http", "sql", "dga", "botnets", "cnn", "roms",
  "datasets", "implementations", "executables", "hyperparameters",
  "antimalware", "pii", "blogposts", "chatbot",
  "r&d", "model(s)", "endpoints", "uis",

  # File extensions
  "pkl", "hdf5", "h5", "pth", "onnx", "tf", "tflite", "yaml", "pb",
  "apk", "apks",

  # Named entities
  # Note that any posessive uses must also be listed here
  "mitre's", "att&ck", "cve",
  "tensorflow", "pytorch", "aws", "colaboratory", "cleverhans", "foolbox", "robustness",
  "sharepoint", "urlnet", "cylance", "cylance's", "proofpoint", "proofpoint's", "imagenet",
  "apktool", "kaspersky", "kaspersky's", "tay's", "c&c", "gpt", "2's", "metame",
  "virustotal", "powershell", "systran", "clearviewai", "clearview", "openai",

  # Other words unrecognized by default
  "i.e.", "e.g.",
  "workspaces", "optimizes", "interleaved", "workloads",
  "reproducibility",  "perceptibility",
  "misclassify", "misclassified", "misclassification", "misclassifications",
  "misconfiguration", "misconfigured",
  "algorithmically", "adversarially",
]

SPELL_CHECKER = SpellChecker()
SPELL_CHECKER.word_frequency.load_words(CUSTOM_WORDS)
