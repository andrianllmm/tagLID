__version__ = "0.0.1"


# Install nltk data

import nltk

try:
    nltk.data.find('tokenizers/punkt.zip')
except LookupError:
    nltk.download("punkt_tab")