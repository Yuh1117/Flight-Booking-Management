from flask import request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime as dt

from . import bookings_bp
from app.blueprints.flights import dao as flight_dao
from app.blueprints.flights import routes as flight_routes
from app.blueprints.auth import dao as auth_dao
from app.blueprints.auth.models import UserRole
from . import dao as booking_dao
from .forms import BookingForm
from .models import Reservation


def validate_flight_seat_class(flight_id, seat_class_id):
    """
    1. Check if flight and seat class are valid
    2. Check if flight has the seat class
    3. Check if there are available seats for the seat class
    """
    flight = flight_dao.get_flight_by_id(flight_id)
    seat_class = flight_dao.get_seat_class_by_id(seat_class_id)
    if not flight or not seat_class:
        flash("Invalid flight or seat class", "danger")
        return False
    remaining_seatclasses_and_info = flight.get_remaining_seatclasses_and_info()
    if seat_class_id not in remaining_seatclasses_and_info:
        flash("Flight doesn't have this seat class", "danger")
        return False
    if remaining_seatclasses_and_info[seat_class_id]["remaining"] == 0:
        flash("No available seats", "danger")
        return False
    return True


@bookings_bp.route("/booking", methods=["GET", "POST"])
@login_required
def reserve_ticket():
    form = BookingForm()
    flight_id = request.args.get("flight", type=int)
    seat_class_id = request.args.get("seat_class", type=int)

    # Check params are valid
    if not validate_flight_seat_class(flight_id, seat_class_id):
        return redirect(url_for("main.home"))

    flight = flight_dao.get_flight_by_id(flight_id)
    seat_class = flight_dao.get_seat_class_by_id(seat_class_id)

    # Fill form with user info if user is customer
    if current_user.role == UserRole.CUSTOMER:
        form.citizen_id.data = current_user.citizen_id

    # if method is POST and form is valid
    if form.validate_on_submit():
        user = auth_dao.get_user_by_citizen_id(form.citizen_id.data)
        flight_seat_id = request.form.get("flight_seat_id", type=int)

        # Check if user has already booked this flight seat whether it is paid or not
        if booking_dao.user_has_booked_flight_seat(user.id, flight_seat_id):
            flash("You have already booked this flight seat", "danger")
            return redirect(url_for("bookings.manage_own_bookings"))

        # Check if flight seat is valid
        flight_seat = flight_dao.get_flight_seat_by_id(flight_seat_id)
        if not flight_seat or flight_seat.is_sold():
            flash("Invalid flight seat or this seat is sold", "danger")
            return redirect(url_for("main.home"))

        flight = flight_seat.flight
        # Check if flight is departed
        if flight.depart_time <= dt.now():
            flash("Flight has already departed", "danger")
            return redirect(url_for("flights.showFlight", id=flight.id))

        # Check if user can book this flight seat
        if current_user.role != UserRole.CUSTOMER:
            min_booking_time = flight_dao.get_staff_min_booking_time()
        else:
            min_booking_time = flight_dao.get_customer_min_booking_time()

        remaining_time_to_book = (
            flight_seat.flight.depart_time - dt.now()
        ).total_seconds() / 60
        if remaining_time_to_book < min_booking_time:
            flash("You are not allowed to book this flight seat", "danger")
            return redirect(url_for("flights.showFlight", id=flight.id))

        # Add reservation
        reservation = booking_dao.add_reservation(
            user.id, current_user.id, flight_seat_id, flight_seat.price
        )
        flash("Reservation created", "success")
        return redirect(url_for("bookings.manage_own_bookings"))

    return render_template(
        "bookings/index.html",
        form=form,
        flight=flight,
        seat_class=seat_class,
        search_time=dt.now(),
        staff_min_booking_time=flight_dao.get_staff_min_booking_time(),
        customer_min_booking_time=flight_dao.get_customer_min_booking_time(),
    )


@bookings_bp.route("/booking/confirmation/<int:reservation_id>", methods=["GET"])
@login_required
def confirmation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    flight_seat = reservation.flight_seat
    flight = flight_seat.flight
    return render_template(
        "bookings/confirmation.html",
        reservation=reservation,
        flight=flight,
        flight_seat=flight_seat,
    )


@bookings_bp.route("/manage-bookings/own")
@login_required
def manage_own_bookings():
    page_num = request.args.get("page", default=1, type=int)
    reservations = booking_dao.get_reservations_of_owned_user(current_user.id, page_num)
    return render_template("bookings/manage_bookings.html", page=reservations)


@bookings_bp.route("/manage-bookings/created-for-others")
@login_required
def manage_bookings_created_for_others():
    page_num = request.args.get("page", default=1, type=int)
    reservations = booking_dao.get_reservations_created_for_others(
        current_user.id, page_num
    )
    return render_template("bookings/manage_bookings.html", page=reservations)
