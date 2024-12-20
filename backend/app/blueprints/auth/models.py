from enum import Enum as BaseEnum
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from app import db


class UserRole(BaseEnum):
    ADMIN = 1
    FLIGHT_MANAGER = 2
    SALES_EMPLOYEE = 3
    CUSTOMER = 4

    def __str__(self):
        return self.name.replace("_", " ").title()


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(db.String(60), nullable=False)
    citizen_id = Column(String(12), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(15), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    avatar = Column(String(120), nullable=True)
    # reservations = relationship("Reservation", backref="user", lazy=True)

    def __repr__(self):
        return (
            f"User('{self.id}', '{self.email}', '{self.role}, '{len(self.password)}')"
        )
