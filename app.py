from flask import Flask
from database.models import db
from routes.auth_routes import auth_bp
from routes.interview_routes import interview_bp
from routes.report_routes import report_bp
import os


def create_app():
    app = Flask(__name__)

    # ==========================
    # BASIC CONFIGURATION
    # ==========================

    app.config["SECRET_KEY"] = "ai_interview_secret_key"

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    app.config["SQLALCHEMY_DATABASE_URI"] = \
        "sqlite:///" + os.path.join(BASE_DIR, "interview.db")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ==========================
    # INITIALIZE DATABASE
    # ==========================

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # ==========================
    # REGISTER BLUEPRINTS
    # ==========================

    app.register_blueprint(auth_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(report_bp)

    return app


# ==========================
# RUN APPLICATION
# ==========================

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)