import re
from difflib import SequenceMatcher


def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text.strip()


def similarity_score(user_answer, correct_answer):
    return SequenceMatcher(None, user_answer, correct_answer).ratio()


def keyword_match_score(user_answer, correct_answer):
    correct_words = set(correct_answer.split())
    user_words = set(user_answer.split())

    if not correct_words:
        return 0

    matches = correct_words.intersection(user_words)
    return len(matches) / len(correct_words)


def evaluate_text_answer(user_answer, correct_answer):

    if not user_answer:
        return 0

    user_answer = preprocess(user_answer)
    correct_answer = preprocess(correct_answer)

    # Similarity ratio (0 to 1)
    sim = similarity_score(user_answer, correct_answer)

    # Keyword match ratio (0 to 1)
    keyword_ratio = keyword_match_score(user_answer, correct_answer)

    # Combine both
    final_ratio = (sim * 0.6) + (keyword_ratio * 0.4)

    # Convert to score out of 10
    score = round(final_ratio * 10)

    return min(score, 10)