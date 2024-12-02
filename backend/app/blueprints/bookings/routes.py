from flask import render_template
from flask_login import login_required
from . import bookings_bp, models


@bookings_bp.route("/booking")
@login_required
def booking():
    """Render the about page."""
    return render_template("main/booking.html")
