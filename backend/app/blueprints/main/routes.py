from flask import render_template
from flask_login import current_user, login_required

# Import the blueprint instance from the `__init__.py`
from . import main_bp
from app import app
from app.blueprints.auth import dao as auth_dao
from app.blueprints.auth import decorators
from app.blueprints.bookings.models import Reservation


@main_bp.route("/")
def home():

    return render_template("main/home.html")


@main_bp.route("/about")
@decorators.admin_required
def about():
    print(current_user.role)
    return render_template("main/about.html", users=auth_dao.get_users())


@main_bp.route("/manage-bookings")
@login_required
def manage_bookings():
    reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    return render_template(
        "managebookings/manage_bookings.html", reservations=reservations
    )
