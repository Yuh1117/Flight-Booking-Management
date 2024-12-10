from flask import render_template
from flask_login import current_user

# Import the blueprint instance from the `__init__.py`
from . import main_bp
from app.blueprints.auth import dao as auth_dao
from app.blueprints.auth import decorators
from app.blueprints.bookings.dao import get_airports

@main_bp.route("/")
def home():
    dataAirport = get_airports()
    return render_template("main/home.html", dataAirport=dataAirport)


@main_bp.route("/about")
@decorators.admin_required
def about():
    print(current_user.role)
    """Render the about page."""
    return render_template("main/about.html", users=auth_dao.get_users())
