def generate_report(session, responses):

    if not responses:
        return {
            "average_score": 0,
            "strength": "Needs improvement",
            "confidence_level": "Low"
        }

    avg_score = sum(r.score for r in responses) / len(responses)
    avg_score = round(avg_score, 2)

    # Strength Logic
    if avg_score >= 8:
        strength = "Strong Technical Depth"
    elif avg_score >= 6:
        strength = "Good Understanding"
    elif avg_score >= 4:
        strength = "Basic Understanding"
    else:
        strength = "Needs improvement"

    # Confidence Logic
    if avg_score >= 8:
        confidence = "High"
    elif avg_score >= 5:
        confidence = "Moderate"
    else:
        confidence = "Low"

    return {
        "average_score": avg_score,
        "strength": strength,
        "confidence_level": confidence
    }