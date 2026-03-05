from difflib import SequenceMatcher

def calculate_plagiarism(responses):

    if not responses:
        return 0

    similarity_scores = []

    for response in responses:
        user_answer = response.answer
        correct_answer = response.correct_answer

        similarity = SequenceMatcher(
            None,
            user_answer.lower(),
            correct_answer.lower()
        ).ratio()

        similarity_scores.append(similarity)

    avg_similarity = sum(similarity_scores) / len(similarity_scores)

    # Convert to percentage
    plagiarism_percentage = round(avg_similarity * 100, 2)

    return plagiarism_percentage