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


def get_user_reservations(user_id, page=1, per_page=app.config["PAGE_SIZE"]):
    return (
        Reservation.query.filter(
            or_(Reservation.user_id == user_id, Reservation.author_id == user_id)
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
