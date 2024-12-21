from sqlalchemy import or_

from .models import *
from app import app


def get_reservation_by_id(reservation_id):
    return Reservation.query.get(reservation_id)


def user_has_booked_flight_seat(user_id, flight_seat_id):
    return (
        Reservation.query.filter_by(
            user_id=user_id, flight_seat_id=flight_seat_id
        ).first()
        is not None
    )


def get_reservations_of_owned_user(user_id, page=1, per_page=app.config["PAGE_SIZE"]):
    return (
        Reservation.query.filter_by(user_id=user_id)
        .order_by(Reservation.created_at.desc())
        .paginate(page=page, per_page=per_page)
    )


def get_reservations_created_for_others(
    author_id, page=1, per_page=app.config["PAGE_SIZE"]
):
    return (
        Reservation.query.filter(
            Reservation.author_id == author_id, Reservation.user_id != author_id
        )
        .order_by(Reservation.created_at.desc())
        .paginate(page=page, per_page=per_page)
    )


def add_reservation(user_id, author_id, flight_seat_id, amount):
    reservation = Reservation(
        user_id=user_id,
        author_id=author_id,
        flight_seat_id=flight_seat_id,
        amount=amount,
    )
    db.session.add(reservation)
    db.session.commit()
    return reservation
