from enum import Enum as BaseEnum
from sqlalchemy import Column, Integer, Enum, ForeignKey, DateTime, Double, String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime as dt

from app import db


class ReservationStatus(BaseEnum):
    PAID = 1
    UNPAID = 2
    CANCELLED = 3

    def __str__(self):
        return self.name.replace("_", " ").title()


class Reservation(db.Model):
    __tablename__ = "reservations"
    __table_args__ = (UniqueConstraint("user_id", "flight_seat_id"),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    flight_seat_id = Column(Integer, ForeignKey("flight_seats.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    amount = Column(Double, nullable=False)
    status = Column(Enum(ReservationStatus), default=ReservationStatus.UNPAID)
    created_at = Column(DateTime, nullable=False, default=dt.utcnow)

    user = relationship(
        "User",
        foreign_keys=[user_id],
        backref="reservations",
    )
    author = relationship(
        "User",
        foreign_keys=[author_id],
        backref="created_reservations",
    )
    flight_seat = relationship("FlightSeat", backref="reservations", lazy=True)

    def __repr__(self):
        return f"Reservation('{self.id}', '{self.flight_seat_id}', '{self.user_id}', '{self.status}')"
