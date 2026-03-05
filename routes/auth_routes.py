from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.models import db, Candidate

auth_bp = Blueprint("auth", __name__)


# ================= HOME =================
@auth_bp.route("/")
def home():
    return redirect(url_for("auth.login"))


# ================= REGISTER =================
@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if Candidate.query.filter_by(email=email).first():
            flash("Email already exists", "error")
            return redirect(url_for("auth.register"))

        user = Candidate(name=name, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ================= LOGIN =================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = Candidate.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session["candidate_id"] = user.id
            return redirect(url_for("interview.dashboard"))

        flash("Invalid email or password", "error")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


# ================= FORGOT PASSWORD =================
@auth_bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":
        email = request.form.get("email")
        new_password = request.form.get("new_password")

        user = Candidate.query.filter_by(email=email).first()

        if not user:
            flash("Email not found", "error")
            return redirect(url_for("auth.forgot_password"))

        user.set_password(new_password)
        db.session.commit()

        flash("Password updated successfully! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")


# ================= LOGOUT =================
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))