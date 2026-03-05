from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from database.models import db, InterviewSession, Response
from ai_engine.question_generator import generate_question
from ai_engine.adaptive_engine import adjust_difficulty
from ai_engine.evaluator import evaluate_text_answer
from ai_engine.fairness import normalize_score

interview_bp = Blueprint("interview", __name__)


# =========================================================
# DASHBOARD
# =========================================================
@interview_bp.route("/dashboard")
def dashboard():
    if "candidate_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("dashboard.html")


# =========================================================
# START INTERVIEW
# =========================================================
@interview_bp.route("/start_interview", methods=["POST"])
def start_interview():

    role = request.form.get("role")
    interview_type = request.form.get("type")

    new_session = InterviewSession(
        candidate_id=session["candidate_id"],
        role=role,
        type=interview_type,
        score=0,
        cheated=False
    )

    db.session.add(new_session)
    db.session.commit()

    session["session_id"] = new_session.id
    session["difficulty"] = "easy"
    session["question_number"] = 1

    # FIX: Clear asked_questions at the start of every new interview
    session_key = f"asked_questions_{new_session.id}"
    session[session_key] = []
    session.modified = True

    q_data = generate_question("easy", role, interview_type)
    session["correct_answer"] = q_data["answer"]

    return render_template(
        "interview.html",
        question=q_data["question"],
        question_number=1,
        total_questions=10
    )


# =========================================================
# SUBMIT ANSWER (AJAX)
# =========================================================
@interview_bp.route("/submit_answer", methods=["POST"])
def submit_answer():

    answer = request.form.get("answer")
    question = request.form.get("question")
    correct_answer = session.get("correct_answer", "")

    raw_score = evaluate_text_answer(answer, correct_answer)
    final_score = normalize_score(raw_score)

    response = Response(
        session_id=session["session_id"],
        question=question,
        answer=answer,
        correct_answer=correct_answer,
        score=final_score
    )

    db.session.add(response)
    # FIX: Commit to DB before calling next_question so response count is accurate
    db.session.commit()

    return next_question()


# =========================================================
# SKIP QUESTION (TIMER)
# =========================================================
@interview_bp.route("/skip_question", methods=["POST"])
def skip_question():

    question = request.form.get("question")

    response = Response(
        session_id=session["session_id"],
        question=question,
        answer="Skipped",
        correct_answer=session.get("correct_answer"),
        score=0
    )

    db.session.add(response)
    # FIX: Commit to DB before calling next_question so response count is accurate
    db.session.commit()

    return next_question()


# =========================================================
# NEXT QUESTION LOGIC
# =========================================================
def next_question():

    responses = Response.query.filter_by(
        session_id=session["session_id"]
    ).all()

    # FIX: Deduplicate responses by question text before counting
    # This prevents already-saved duplicate DB entries from inflating the count
    seen = set()
    unique_responses = []
    for r in responses:
        if r.question not in seen:
            seen.add(r.question)
            unique_responses.append(r)

    question_count = len(unique_responses)

    if question_count >= 10:

        avg = sum(r.score for r in unique_responses) / question_count

        interview_session = InterviewSession.query.get(session["session_id"])
        interview_session.score = round(avg, 2)

        db.session.commit()

        return jsonify({"completed": True})

    last_score = unique_responses[-1].score
    new_difficulty = adjust_difficulty(last_score)

    interview_session = InterviewSession.query.get(session["session_id"])

    # FIX: Pass the already-answered question texts so generate_question
    # can avoid them even if the session key somehow missed one
    already_asked = [r.question for r in unique_responses]
    session_key = f"asked_questions_{session['session_id']}"

    # Merge DB-level asked list with session-level asked list for full accuracy
    merged_asked = list(set(session.get(session_key, []) + already_asked))
    session[session_key] = merged_asked
    session.modified = True

    q_data = generate_question(
        new_difficulty,
        interview_session.role,
        interview_session.type
    )

    session["correct_answer"] = q_data["answer"]
    session["question_number"] = question_count + 1
    session.modified = True

    return jsonify({
        "completed": False,
        "question": q_data["question"],
        "question_number": session["question_number"]
    })


# =========================================================
# FORCE SUBMIT (CHEATING)
# =========================================================
@interview_bp.route("/force_submit", methods=["GET"])
def force_submit():

    interview_session = InterviewSession.query.get(session["session_id"])
    interview_session.cheated = True

    responses = Response.query.filter_by(
        session_id=session["session_id"]
    ).all()

    question_count = len(responses)

    while question_count < 10:
        response = Response(
            session_id=session["session_id"],
            question="Security violation",
            answer="No Answer",
            correct_answer="N/A",
            score=0
        )
        db.session.add(response)
        question_count += 1

    db.session.commit()

    responses = Response.query.filter_by(
        session_id=session["session_id"]
    ).all()

    avg = sum(r.score for r in responses) / len(responses)
    interview_session.score = round(avg, 2)

    db.session.commit()

    return redirect(url_for("report.view_report"))
