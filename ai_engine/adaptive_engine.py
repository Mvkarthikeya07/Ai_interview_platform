def adjust_difficulty(previous_score):
    if previous_score >= 8:
        return "hard"
    elif previous_score >= 5:
        return "medium"
    else:
        return "easy"