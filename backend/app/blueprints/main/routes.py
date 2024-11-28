from flask import render_template

# Import the blueprint instance from the `__init__.py`
from . import main_bp
from app.blueprints.auth import dao as auth_dao


@main_bp.route("/")
def home():
    """Render the home page."""
    return render_template("main/home.html")


@main_bp.route("/about")
def about():
    """Render the about page."""
    return render_template("main/about.html", users=auth_dao.get_users())


@main_bp.route("/booking")
def booking():
    """Render the about page."""
    return render_template("main/booking.html")


@main_bp.route("/dashboard")
def admin():
    """Render the about page."""
    return render_template("admin/dashboard.html")