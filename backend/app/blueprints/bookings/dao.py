from sqlalchemy import or_

from .models import *
from app import app


def get_reservation_by_id(reservation_id):
    return Reservation.query.get(reservation_id)


def get_user_reservation_by_flight_seat(user, flight_seat):
    return next((r for r in user.reservations if r.flight_seat == flight_seat), None)


def get_reservations_of_owned_user(owner_id, page=1, per_page=app.config["PAGE_SIZE"]):
    return (
        Reservation.query.filter_by(owner_id=owner_id)
        .order_by(Reservation.created_at.desc())
        .paginate(page=page, per_page=per_page)
    )


def get_reservations_created_for_others(
    author_id, page=1, per_page=app.config["PAGE_SIZE"]
):
    return (
        Reservation.query.filter(
            Reservation.author_id == author_id, Reservation.owner_id != author_id
        )
        .order_by(Reservation.created_at.desc())
        .paginate(page=page, per_page=per_page)
    )


def add_reservation(owner_id, author_id, flight_seat_id):
    reservation = Reservation(
        owner_id=owner_id,
        author_id=author_id,
        flight_seat_id=flight_seat_id,
    )
    db.session.add(reservation)
    db.session.commit()
    return reservation


def delete_reservation_of_user(owner_id, reservation_id):
    reservation = Reservation.query.filter(
        (Reservation.id == reservation_id) & (Reservation.owner_id == owner_id)
    ).first()
    if not reservation:
        return False
    db.session.delete(reservation)
    db.session.commit()
    return True


def get_reservation_by_id_and_user(id, user_id):
    return Reservation.query.filter(
        (Reservation.id == id)
        & ((Reservation.owner_id == user_id) | (Reservation.author_id == user_id))
    ).first()


def update_reservation_seat(reservation, flight_seat_id):
    reservation.flight_seat_id = flight_seat_id
    db.session.commit()
    return reservation
