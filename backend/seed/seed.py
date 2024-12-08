import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime as dt
import json
from sqlalchemy import inspect
from app import app, db
from app.blueprints.auth import dao as auth_dao
from app.blueprints.auth.models import UserRole
from app.blueprints.flights.models import Route
from app.blueprints.flights.models import Airport
from app.blueprints.flights.models import Country
from app.blueprints.flights.models import Flight
from app.blueprints.flights.models import Airline
from app.blueprints.flights.models import Aircraft
from app.blueprints.flights.models import IntermediateAirport
from app.blueprints.flights.dao import find_intermediate_airport

def seed_users():
    with open("backend/seed/data/users.json") as f:
        users = json.load(f)
        for user in users:
            user["role"] = UserRole(user["role"])
            auth_dao.add_user(**user)


def seed_routes():
    try:
        with open("backend/seed/data/routes.json") as f:
            routes = json.load(f)
        for route in routes:
            print(route)
            existing_route = Route.query.filter_by(
                name=route['name'],
                depart_airport_id=route["depart_airport_id"],
                arrive_airport_id=route["arrive_airport_id"],
            ).first()

            if not existing_route:
                new_route = Route(
                    id=route["id"],
                    name=route['name'],
                    depart_airport_id=route["depart_airport_id"],
                    arrive_airport_id=route["arrive_airport_id"],
                )
                db.session.add(new_route)  # Thêm vào session

        # Commit các thay đổi
        db.session.commit()
        print("Routes seeded successfully!")
    except Exception as e:
        db.session.rollback()  # Rollback nếu có lỗi xảy ra
        print(f"Failed to seed routes: {e}")


def seed_airports():
    try:
        with open("backend/seed/data/airportsFull.json") as f:
            airports = json.load(f)
        for airport in airports:
            print(airport)
            existing_airport = Airport.query.filter_by(code=airport["code"]).first()
            if not existing_airport:
                # Tạo đối tượng Airport mới
                new_airport = Airport(
                    id=airport["id"],
                    name=airport["name"],
                    code=airport["code"],
                    country_id=airport["country_id"],
                )
                db.session.add(new_airport)  # Thêm vào session

        # Commit các thay đổi
        db.session.commit()
        print("Airports seeded successfully!")
    except Exception as e:
        db.session.rollback()  # Rollback nếu có lỗi xảy ra
        print(f"Failed to seed airports: {e}")


def seed_countries():
    try:
        with open("backend/seed/data/countries.json") as f:
            countries = json.load(f)
        for country in countries:
            print(country)
            existing_country = Country.query.filter_by(
                code=country["CountryCode"]
            ).first()
            if not existing_country:
                # Tạo đối tượng Country mới
                new_country = Country(
                    id=country["id"], name=country["name"], code=country["CountryCode"]
                )
                db.session.add(new_country)  # Thêm vào session

        # Commit các thay đổi
        db.session.commit()
        print("Countries seeded successfully!")
    except Exception as e:
        db.session.rollback()  # Rollback nếu có lỗi xảy ra
        print(f"Failed to seed countries: {e}")


def seed_flights():
    try:
        with open("backend/seed/data/flights.json") as f:
            flights = json.load(f)
        for flight in flights:
            existing_flight = Flight.query.filter_by(id=flight["id"]).first()

            if not existing_flight:
                # Chuyển đổi thời gian từ định dạng chuỗi sang đối tượng datetime
                depart_time = datetime.fromisoformat(
                    flight["depart_time"].replace("Z", "+00:00")
                )
                arrive_time = datetime.fromisoformat(
                    flight["arrive_time"].replace("Z", "+00:00")
                )

                new_flight = Flight(
                    id=flight["id"],
                    route_id=flight["route_id"],
                    depart_time=depart_time,
                    arrive_time=arrive_time,
                    aircraft_id=flight["aircraft_id"],
                )
                db.session.add(new_flight)  # Thêm vào session

        # Commit các thay đổi
        db.session.commit()
        print("Flights seeded successfully!")
    except Exception as e:
        db.session.rollback()  # Rollback nếu có lỗi xảy ra
        print(f"Failed to seed flights: {e}")


def seed_airlines():
    try:
        with open("backend/seed/data/airlines.json") as f:
            airlines = json.load(f)
        for airline in airlines:
            existing_airline = Airline.query.filter_by(id=airline["id"]).first()

            if not existing_airline:
                # Tạo đối tượng Airline mới
                new_airline = Airline(id=airline["id"], name=airline["name"])
                db.session.add(new_airline)  # Thêm vào session
        db.session.commit()
        print("Airlines seeded successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Failed to seed airlines: {e}")


def seed_aircrafts():
    try:
        with open("backend/seed/data/aircrafts.json") as f:
            aircrafts = json.load(f)
        for aircraft in aircrafts:
            existing_aircraft = Aircraft.query.filter_by(id=aircraft["id"]).first()

            if not existing_aircraft:
                new_aircraft = Aircraft(
                    id=aircraft["id"],
                    airline_id=aircraft["airline"],  # Hãng hàng không
                    name=aircraft["name"],
                )
                db.session.add(new_aircraft)  # Thêm vào session

        # Commit các thay đổi
        db.session.commit()
        print("Aircrafts seeded successfully!")
    except Exception as e:
        db.session.rollback()  # Rollback nếu có lỗi xảy ra
        print(f"Failed to seed aircrafts: {e}")

def seed_intermediate_airport():
    try:
        with open("backend/seed/data/stops.json") as f:
            intermediate_airports = json.load(f)
        for intermediate_airport in intermediate_airports:
            existing_intermediate_airport = IntermediateAirport.query.filter_by(
                flight_id=intermediate_airport["flight_id"],
                airport_id=intermediate_airport["airport_id"],
            ).first()
            if not existing_intermediate_airport:
                new_intermediate_airport = IntermediateAirport(
                        airport_id=intermediate_airport["airport_id"],
                        flight_id=intermediate_airport["flight_id"],
                        arrival_time=datetime.fromisoformat(intermediate_airport["arrive_time"].replace("Z", "")),
                        departure_time=datetime.fromisoformat(intermediate_airport["depart_time"].replace("Z", "")),
                        order=intermediate_airport["order"],
                )
                db.session.add(new_intermediate_airport)  # Thêm vào session
                print(new_intermediate_airport.to_dict())
        db.session.commit()
        print("Intermediate airports seeded successfully!")
    except Exception as e:
        db.session.rollback()  # Rollback nếu có lỗi xảy ra
        print(f"Failed to seed intermediate airports: {e}")
     
if __name__ == "__main__":

    with app.app_context():
        db.create_all()
        seed_users()
        seed_countries()
        seed_airports()
        seed_routes()
        seed_flights()
        seed_airlines()
        seed_aircrafts()
        seed_intermediate_airport()
        db.session.commit()
        print("Data seeded successfully.")
        print(inspect(db.engine).get_table_names())
