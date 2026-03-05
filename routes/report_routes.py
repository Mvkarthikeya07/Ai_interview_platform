from flask import Blueprint, render_template, session, redirect, url_for
from database.models import db, InterviewSession, Response
from ai_engine.plagiarism import calculate_plagiarism

report_bp = Blueprint("report", __name__)


# =========================================================
# INTERVIEW REPORT
# =========================================================
@report_bp.route("/report")
def view_report():

    if "session_id" not in session:
        return redirect(url_for("interview.dashboard"))

    interview_session = InterviewSession.query.get(session["session_id"])

    if not interview_session:
        return redirect(url_for("interview.dashboard"))

    responses = Response.query.filter_by(
        session_id=session["session_id"]
    ).all()

    # ============================
    # OVERALL SCORE
    # ============================
    overall_score = interview_session.score

    # ============================
    # STRENGTH & CONFIDENCE LOGIC
    # ============================
    if overall_score >= 8:
        strength = "Strong Technical Depth"
        confidence = "High"
    elif overall_score >= 6:
        strength = "Good Understanding"
        confidence = "Moderate"
    elif overall_score >= 4:
        strength = "Basic Understanding"
        confidence = "Moderate"
    else:
        strength = "Needs improvement"
        confidence = "Low"

    # ============================
    # RADAR METRICS
    # ============================
    technical = round(overall_score, 2)
    clarity = round(overall_score * 0.8, 2)
    problem_solving = round(overall_score * 0.9, 2)
    confidence_metric = round(overall_score * 0.85, 2)

    # ============================
    # PLAGIARISM %
    # ============================
    plagiarism_percent = calculate_plagiarism(responses)

    # ============================
    # FEEDBACK LOGIC
    # ============================
    if overall_score >= 8:
        feedback_title = "🌟 Outstanding Performance!"
        feedback_badge = "top"
        feedback_summary = (
            "You demonstrated exceptional technical knowledge and strong problem-solving skills. "
            "Your answers reflected clarity, depth, and confidence. You are well-prepared for real-world interviews."
        )
        feedback_points = [
            "Explore system design and architecture patterns to strengthen senior-level readiness.",
            "Contribute to open-source projects to build a stronger portfolio.",
            "Practice mock interviews to maintain your edge under pressure.",
            "Dive deeper into advanced topics like distributed systems, concurrency, and scalability.",
            "Prepare compelling stories for behavioural questions using the STAR method."
        ]
        feedback_color = "green"

    elif overall_score >= 6:
        feedback_title = "👍 Good Job — Keep Pushing!"
        feedback_badge = "good"
        feedback_summary = (
            "You showed a solid understanding of core concepts and handled most questions well. "
            "With focused practice on weaker areas, you can reach an outstanding level."
        )
        feedback_points = [
            "Revisit topics where your score was below 7 and practice similar questions.",
            "Work on structuring your answers more clearly — use the STAR or PREP method.",
            "Strengthen problem-solving by practising LeetCode medium-level questions daily.",
            "Improve confidence by doing timed mock interviews regularly.",
            "Build small projects to apply theoretical knowledge practically."
        ]
        feedback_color = "blue"

    elif overall_score >= 4:
        feedback_title = "⚠️ Average Performance — Room to Grow"
        feedback_badge = "average"
        feedback_summary = (
            "You have a basic understanding of the topics but struggled with depth and clarity in several areas. "
            "Consistent study and hands-on practice will significantly improve your performance."
        )
        feedback_points = [
            "Go back to fundamentals — revisit core concepts for your role.",
            "Study the correct answers provided in the breakdown above carefully.",
            "Practice coding or scenario-based questions for at least 30 minutes daily.",
            "Focus on communicating your thought process clearly, not just the final answer.",
            "Take free online courses or tutorials to fill knowledge gaps.",
            "Join study groups or communities to learn from peers."
        ]
        feedback_color = "orange"

    else:
        feedback_title = "❗ Needs Significant Improvement"
        feedback_badge = "low"
        feedback_summary = (
            "Your responses suggest a need to revisit foundational concepts for this role. "
            "Don't be discouraged — with a structured study plan and consistent effort, improvement is absolutely achievable."
        )
        feedback_points = [
            "Start from the basics — study core fundamentals of your chosen role thoroughly.",
            "Read through every correct answer in the report above and make notes.",
            "Follow a structured learning path: pick one resource (course, book, or roadmap) and stick to it.",
            "Practice at least 3–5 questions per day and gradually increase difficulty.",
            "Focus on understanding concepts deeply rather than memorising answers.",
            "Schedule regular mock interviews to track your progress over time.",
            "Reach out to a mentor or join a community for guidance and accountability."
        ]
        feedback_color = "red"

    return render_template(
        "report.html",
        session=interview_session,
        responses=responses,
        overall_score=overall_score,
        strength=strength,
        confidence=confidence,
        technical=technical,
        clarity=clarity,
        problem_solving=problem_solving,
        confidence_metric=confidence_metric,
        plagiarism=plagiarism_percent,
        feedback_title=feedback_title,
        feedback_badge=feedback_badge,
        feedback_summary=feedback_summary,
        feedback_points=feedback_points,
        feedback_color=feedback_color
    )


# =========================================================
# PROGRESS PAGE
# =========================================================
@report_bp.route("/progress")
def view_progress():

    if "candidate_id" not in session:
        return redirect(url_for("auth.login"))

    sessions = InterviewSession.query.filter_by(
        candidate_id=session["candidate_id"]
    ).order_by(InterviewSession.created_at.desc()).all()

    return render_template(
        "progress.html",
        sessions=sessions
    )
