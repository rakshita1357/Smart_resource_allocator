from typing import List
import re

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
except Exception:
    nltk = None
    stopwords = None
    word_tokenize = None


def _ensure_nltk():
    if nltk is None:
        return
    try:
        stopwords.words("english")
    except Exception:
        nltk.download("punkt")
        nltk.download("stopwords")


def clean_text(text: str) -> List[str]:
    """Clean text: lowercase, remove punctuation, tokenize, remove stopwords.

    Returns list of tokens.
    """
    if not text:
        return []

    _ensure_nltk()

    # Lowercase
    t = text.lower()

    # Remove punctuation and non-word characters
    t = re.sub(r"[^a-z0-9\s]", " ", t)

    # Tokenize
    if word_tokenize:
        tokens = word_tokenize(t)
    else:
        tokens = t.split()

    # Remove stopwords
    if stopwords:
        sw = set(stopwords.words("english"))
        tokens = [tok for tok in tokens if tok not in sw and tok.isalpha()]
    else:
        tokens = [tok for tok in tokens if tok.isalpha()]

    return tokens
# in process
