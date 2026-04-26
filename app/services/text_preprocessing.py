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


_FALLBACK_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "if",
    "in",
    "into",
    "is",
    "it",
    "no",
    "not",
    "of",
    "on",
    "or",
    "such",
    "that",
    "the",
    "their",
    "then",
    "there",
    "these",
    "they",
    "this",
    "to",
    "was",
    "will",
    "with",
    "we",
    "you",
    "your",
    "from",
    "our",
    "has",
    "have",
    "had",
    "were",
    "been",
    "can",
    "could",
    "should",
    "would",
    "may",
    "might",
    "do",
    "does",
    "did",
}


def _safe_stopwords() -> set[str]:
    """Return a stopword set without requiring runtime corpus downloads."""
    if stopwords is None:
        return _FALLBACK_STOPWORDS

    try:
        return set(stopwords.words("english"))
    except Exception:
        return _FALLBACK_STOPWORDS


def _tokenize(text: str) -> list[str]:
    """Tokenize text using NLTK when available, otherwise use a regex fallback."""
    if word_tokenize is not None:
        try:
            return word_tokenize(text)
        except LookupError:
            pass
        except Exception:
            pass

    return re.findall(r"\b[a-z0-9]+\b", text)


def clean_text(text: str) -> List[str]:
    """Clean text by lowercasing, removing punctuation, tokenizing, and filtering stopwords.

    The function is resilient to missing NLTK corpora and will fall back to a
    deterministic regex tokenizer plus a built-in English stopword list.
    """
    if not text:
        return []

    # Lowercase
    t = text.lower()

    # Normalize punctuation/non-word characters to spaces
    t = re.sub(r"[^a-z0-9\s]", " ", t)

    # Tokenize with a safe fallback
    tokens = _tokenize(t)

    # Remove stopwords and keep alphabetic tokens only
    sw = _safe_stopwords()
    cleaned_tokens = [tok for tok in tokens if tok not in sw and tok.isalpha()]

    return cleaned_tokens
# in process
