import re
from difflib import SequenceMatcher


# =========================================================
# PREPROCESSING
# =========================================================

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text.strip()


# =========================================================
# GIBBERISH / NOISE DETECTION
# =========================================================

# Common English words — if the answer contains NONE of these,
# it is treated as gibberish and scores 0 immediately.
COMMON_WORDS = {
    "the", "is", "are", "was", "were", "a", "an", "of", "to", "in",
    "it", "for", "on", "with", "as", "at", "by", "from", "that", "this",
    "be", "have", "has", "had", "do", "does", "did", "not", "but", "and",
    "or", "so", "if", "we", "you", "i", "he", "she", "they", "can", "will",
    "use", "used", "when", "how", "what", "which", "who", "its", "also",
    "been", "than", "then", "one", "two", "all", "each", "more", "into",
    "may", "should", "could", "would", "must", "data", "code", "system",
    "function", "class", "object", "method", "value", "type", "return",
    "list", "array", "key", "set", "map", "get", "output", "input", "result"
}

def is_gibberish(text):
    """
    Returns True if the answer looks like random keystrokes:
    - Fewer than 3 words, OR
    - No word longer than 2 chars that exists in common vocabulary
    """
    words = text.split()

    # Too short to be a real answer
    if len(words) < 3:
        return True

    # Check if at least one real word exists in the answer
    real_word_found = any(w in COMMON_WORDS for w in words)
    if real_word_found:
        return False

    # If no common word found, check average word length —
    # gibberish tends to be one long random string or very short tokens
    avg_len = sum(len(w) for w in words) / len(words)
    if avg_len < 3 or avg_len > 12:
        return True

    # Count how many words are "pronounceable" (have at least one vowel)
    vowels = set("aeiou")
    pronounceable = sum(1 for w in words if any(c in vowels for c in w))
    if pronounceable / len(words) < 0.5:
        return True

    return False


# =========================================================
# SCORING HELPERS
# =========================================================

def similarity_score(user_answer, correct_answer):
    return SequenceMatcher(None, user_answer, correct_answer).ratio()


def keyword_match_score(user_answer, correct_answer):
    correct_words = set(correct_answer.split())
    user_words = set(user_answer.split())

    if not correct_words:
        return 0

    matches = correct_words.intersection(user_words)
    return len(matches) / len(correct_words)


# =========================================================
# MAIN EVALUATOR
# =========================================================

def evaluate_text_answer(user_answer, correct_answer):

    if not user_answer or not user_answer.strip():
        return 0

    user_clean    = preprocess(user_answer)
    correct_clean = preprocess(correct_answer)

    # Reject gibberish / random keystrokes immediately
    if is_gibberish(user_clean):
        return 0

    # Similarity ratio (0 to 1)
    sim = similarity_score(user_clean, correct_clean)

    # Keyword match ratio (0 to 1)
    keyword_ratio = keyword_match_score(user_clean, correct_clean)

    # Combine both
    final_ratio = (sim * 0.6) + (keyword_ratio * 0.4)

    # Convert to score out of 10
    score = round(final_ratio * 10)

    return min(score, 10)
