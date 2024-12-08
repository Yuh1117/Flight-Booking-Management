from sqlalchemy import (
    Column,
    Integer,
    String,
    VARCHAR,
    ForeignKey,
    DateTime,
    Double,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from app import db


class Country(db.Model):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    code = Column(VARCHAR(5), unique=True, nullable=False)
    airports = relationship("Airport", backref="country", lazy=True)

    def __repr__(self):
        return f"Country({self.id}, '{self.name}', '{self.code}')"


class Airport(db.Model):
    __tablename__ = "airports"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    code = Column(VARCHAR(5), unique=True, nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=True)

    def __repr__(self):
        return f"Airport({self.id}, '{self.name}', '{self.code}', '{self.country_id}')"

    @property
    def country_name(self):
        return self.country.name if self.country else None


class Airline(db.Model):
    __tablename__ = "airlines"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    aircrafts = relationship("Aircraft", backref="airline", lazy=True)

    def __repr__(self):
        return f"Airline({self.id}, '{self.name}')"


class Aircraft(db.Model):
    __tablename__ = "aircrafts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=False)
    seats = relationship("AircraftSeat", backref="aircraft", lazy=True)

    def __repr__(self):
        return f"Aircraft({self.id}, '{self.airline.name}', '{self.name}')"

    def is_available(self, depart_time, arrive_time):
        for flight in self.flights:
            if flight.depart_time < arrive_time and flight.arrive_time > depart_time:
                return False
        return True

    @property
    def airline_name(self):
        return self.airline.name if self.airline else "N/A"


class SeatClass(db.Model):
    __tablename__ = "seat_classes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    def __repr__(self):
        return f"SeatClass({self.id}, '{self.name}')"


class AircraftSeat(db.Model):
    __tablename__ = "aircraft_seats"
    id = Column(Integer, primary_key=True, autoincrement=True)
    aircraft_id = Column(Integer, ForeignKey("aircrafts.id"), nullable=False)
    seat_class_id = Column(Integer, ForeignKey("seat_classes.id"), nullable=False)
    seat_name = Column(String(5), nullable=False)
    seat_class = relationship("SeatClass", backref="seats", lazy=True)

    def __repr__(self):
        return f"AircraftSeat({self.id}, {self.aircraft}, '{self.seat_class.name}', '{self.seat_name}')"


class FlightSeat(db.Model):
    __tablename__ = "flight_seats"
    id = Column(Integer, primary_key=True, autoincrement=True)
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=False)
    aircraft_seat_id = Column(Integer, ForeignKey("aircraft_seats.id"), nullable=False)
    price = Column(Double, nullable=False)
    currency = Column(VARCHAR(20), nullable=False)
    aircraft_seat = relationship("AircraftSeat", backref="flight_seats", lazy=True)

    def __repr__(self):
        return f"FlightSeat({self.id}, Flight-{self.flight_id}, '{self.aircraft_seat.seat_name}', '{self.aircraft_seat.seat_class.name}', {self.price}-{self.currency})"


class Route(db.Model):
    __tablename__ = "routes"
    __table_args__ = (
        UniqueConstraint("depart_airport_id", "arrive_airport_id", name="unique_route"),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    depart_airport_id = Column(
        Integer, ForeignKey("airports.id", ondelete="CASCADE"), nullable=False
    )
    arrive_airport_id = Column(
        Integer, ForeignKey("airports.id", ondelete="CASCADE"), nullable=False
    )
    depart_airport = relationship("Airport", foreign_keys=[depart_airport_id])
    arrive_airport = relationship("Airport", foreign_keys=[arrive_airport_id])
    flights = relationship("Flight", backref="route", lazy=True)

    def __repr__(self):
        return f"Route({self.id}, '{self.depart_airport}', '{self.arrive_airport}')"

    @property
    def depart_airport_name(self):
        return self.depart_airport.name if self.depart_airport else None

    @property
    def arrive_airport_name(self):
        return self.arrive_airport.name if self.arrive_airport else None

    def to_dict(self):
        return {
            "id": self.id,
            "depart_airport": self.depart_airport_name,
            "arrive_airport": self.arrive_airport_name,
        }


class Flight(db.Model):
    __tablename__ = "flights"
    id = Column(Integer, primary_key=True, autoincrement=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    depart_time = Column(DateTime, nullable=False)
    arrive_time = Column(DateTime, nullable=False)
    aircraft_id = Column(Integer, ForeignKey("aircrafts.id"), nullable=False)
    aircraft = relationship("Aircraft", backref="flights", lazy=True)
    flight_seats = relationship("FlightSeat", backref="flight", lazy=True)

    __table_args__ = (
        CheckConstraint("depart_time < arrive_time", name="check_depart_time"),
    )

    def __repr__(self):
        return f"Flight({self.id}, {self.route}, '{self.depart_time}', '{self.arrive_time}', {self.aircraft})"

    def to_dict(self):
        return {
            "id": self.id,
            "route_id": self.route_id,
            "depart_time": self.depart_time.isoformat(),
            "arrive_time": self.arrive_time.isoformat(),
            "aircraft_id": self.aircraft_id,
        }
