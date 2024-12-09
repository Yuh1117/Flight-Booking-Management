from enum import Enum as BaseEnum
from sqlalchemy import Column, Integer, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.blueprints.flights.models import FlightSeat
from app.blueprints.auth.models import User
from enum import Enum as PyEnum
from sqlalchemy.sql import func
from app import db


class ReservationStatus(BaseEnum):
    UNPAID = 1
    PAID = 2
    CANCELLED = 3

    def __str__(self):
        return self.name.replace("_", " ").title()


class Reservation(db.Model):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    flight_seat_id = Column(Integer, ForeignKey("flight_seats.id"), nullable=False)
    status = Column(Enum(ReservationStatus), default=ReservationStatus.UNPAID)
    created_at = Column(DateTime, nullable=False)

    def __repr__(self):
        return f"Reservation('{self.id}', '{self.flight_seat_id}', '{self.user_id}', '{self.status}')"
    

