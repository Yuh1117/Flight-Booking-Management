from datetime import datetime as dt

from .models import *
from .models import Route, Flight, Airport, IntermediateAirport , db, Aircraft
from app import app


def add_route(depart_airport_id, arrive_airport_id):
    # Tạo đối tượng Route mới
    new_route = Route(
        depart_airport_id=depart_airport_id,
        arrive_airport_id=arrive_airport_id,
    )

    # Thêm vào session của SQLAlchemy
    db.session.add(new_route)

    try:
        # commit dữ liệu vào cơ sở dữ liệu
        db.session.commit()
        print("New route added successfully!")
        return new_route
    except Exception as e:
        # Rollback nếu có lỗi xảy ra
        db.session.rollback()
        print(f"Failed to add new route: {e}")
        return None


def add_flight(
    route_id,
    depart_time: dt,
    arrive_time: dt,
    aircraft_id,
):
    if depart_time >= arrive_time:
        raise ValueError("Depart time must be less than arrive time")
    # Check flight duration
    flight_minutes = (arrive_time - depart_time).seconds // 60
    min_f_duration = get_min_flight_duration()
    max_f_duration = get_max_flight_duration()
    if not min_f_duration <= flight_minutes <= max_f_duration:
        raise ValueError(
            f"Flight duration must be between {min_f_duration} - {max_f_duration} minutes!"
        )

    new_flight = Flight(
        route_id=route_id,
        depart_time=depart_time,
        arrive_time=arrive_time,
        aircraft_id=aircraft_id,
    )

    db.session.add(new_flight)

    try:
        # commit dữ liệu vào cơ sở dữ liệu
        db.session.commit()
        return new_flight
    except Exception as e:
        db.session.rollback()
        return None


def add_intermediate_airport(
    airport_id, flight_id, arrival_time, departure_time, order
):
    new_intermediate_airport = IntermediateAirport(
        airport_id=airport_id,
        flight_id=flight_id,
        arrival_time=arrival_time,
        departure_time=departure_time,
        order=order,
    )

    db.session.add(new_intermediate_airport)

    try:
        db.session.commit()
        return new_intermediate_airport
    except Exception as e:
        db.session.rollback()
        return None


def load_routes(kw_depart_airport=None, kw_arrive_airport=None, page=None):
    query = Route.query
    if kw_depart_airport:
        query = query.filter(Route.depart_airport_id == int(kw_depart_airport))
        
    if kw_arrive_airport:
        query = query.filter(Route.arrive_airport_id == int(kw_arrive_airport))
        

    page_size = app.config["PAGE_SIZE"]
    start = (page - 1) * page_size
    query = query.slice(start, start + page_size)

    return query.all()


def get_country_by_code(code):
    return Country.query.filter(Country.code.ilike(code)).first()


def get_airport_by_code(code):
    return Airport.query.filter(Airport.code.ilike(code)).first()


def get_route_by_airports(depart_airport_id, arrive_airport_id):
    return Route.query.filter(
        Route.depart_airport_id == depart_airport_id,
        Route.arrive_airport_id == arrive_airport_id,
    ).first()


def count_routes(kw_depart_airport=None, kw_arrive_airport=None):
    query = Route.query
    if kw_depart_airport and kw_arrive_airport:
        return query.filter(Route.depart_airport_id == int(kw_depart_airport), Route.arrive_airport_id == int(kw_arrive_airport)).count()
    elif kw_depart_airport:
        return query.filter(
            Route.depart_airport_id == int(kw_depart_airport)).count()
    elif kw_arrive_airport:
        return query.filter(
            Route.arrive_airport_id == int(kw_arrive_airport)).count()

    return Route.query.count()


def get_route_by_id(id):
    return Route.query.get(id)


# not stopover airport
def load_stopover_airport():
    return Airport.query.all()


def load_airports(id_depart_airport=None, id_arrive_airport=None):
    return Airport.query.filter(
        Airport.id != id_depart_airport, Airport.id != id_arrive_airport
    ).all()


def load_flights(page=None):
    query = Flight.query.order_by(Flight.id.desc())

    page_size = app.config["PAGE_SIZE"]
    start = (page - 1) * page_size
    query = query.slice(start, start + page_size)

    return query.all()


def count_flights():
    return Flight.query.count()


def find_intermediate_airport(flight_id):
    # Tìm tất cả sân bay trung gian của một chuyến bay cụ thể
    intermediate_airports = IntermediateAirport.query.filter(
        IntermediateAirport.flight_id == flight_id
    ).all()
    # Trả về kết quả dưới dạng danh sách dictionary
    return [
        intermediate_airport.to_dict() for intermediate_airport in intermediate_airports
    ]


# def find_airport(kw):
#     airport_ids = [
#         airport_id[0]
#         for airport_id in Airport.query.filter(Airport.name.contains(kw))
#         .with_entities(Airport.id)
#         .all()
#     ]
#     return airport_ids


def load_aircarfts():
    return Aircraft.query.all()


def get_min_flight_duration():
    return (
        Regulation.query.filter(Regulation.key == "min_flight_duration").first().value
    )


def get_max_flight_duration():
    return (
        Regulation.query.filter(Regulation.key == "max_flight_duration").first().value
    )

def get_max_stopover_airports():
    return Regulation.query.filter(Regulation.key == 'max_stopover_airports').first().value
