from .models import Route, Flight, Airport, IntermediateAirport , db, Aircraft
from app import app


def add_route(
    depart_airport_id,
    arrive_airport_id,
    depart_airport,
    arrive_airport,
    flights
):
    # Tạo đối tượng Route mới
    new_route = Route(
        depart_airport_id=depart_airport_id,
        arrive_airport_id=arrive_airport_id,
        depart_airport=depart_airport,
        arrive_airport=arrive_airport,
        flights=flights
    )

    # Thêm vào session của SQLAlchemy
    db.session.add(new_route)
    
    try:
        #commit dữ liệu vào cơ sở dữ liệu
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
    depart_time,
    arrive_time,
    aircraft_id,
):
    new_flight = Flight(
        route_id=route_id,
        depart_time=depart_time,
        arrive_time=arrive_time,
        aircraft_id=aircraft_id,
    )

    db.session.add(new_flight)
    
    try:
        db.session.commit()
        return new_flight
    except Exception as e:
        db.session.rollback()
        return None

def add_intermediate_airport(
    airport_id,
    flight_id,
    arrival_time,
    departure_time,
    order
):
    new_intermediate_airport = IntermediateAirport(
        airport_id=airport_id,
        flight_id=flight_id,
        arrival_time=arrival_time,
        departure_time=departure_time,
        order=order
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
        query = query.filter(Route.depart_airport_id.in_(find_airport(kw_depart_airport)))
    if kw_arrive_airport:
        query = query.filter(Route.arrive_airport_id.in_(find_airport(kw_arrive_airport)))

    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    query = query.slice(start, start + page_size)
    
    return query.all()

def count_routes(kw_depart_airport=None, kw_arrive_airport=None):
    query = Route.query
    if kw_depart_airport and kw_arrive_airport:
        query = query.filter(Route.depart_airport_id.in_(find_airport(kw_depart_airport)))
        query = query.filter(Route.arrive_airport_id.in_(find_airport(kw_arrive_airport)))
        return query.count()
    elif kw_depart_airport:
        return query.filter(Route.depart_airport_id.in_(find_airport(kw_depart_airport))).count()
    elif kw_arrive_airport:
        return query.filter(Route.arrive_airport_id.in_(find_airport(kw_arrive_airport))).count()

    return Route.query.count()

def get_route_by_id(id):
    return Route.query.get(id)

def load_airports(id_depart_airport=None, id_arrive_airport=None):
    return Airport.query.filter(Airport.id != id_depart_airport, Airport.id != id_arrive_airport).all()

def load_flights(page=None):
    query = Flight.query.order_by(Flight.id.desc())
    
    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    query = query.slice(start, start + page_size)

    return query.all() 

def count_flights():
    return Flight.query.count()

def find_intermediate_airport(flight_id):
    # Tìm tất cả sân bay trung gian của một chuyến bay cụ thể
    intermediate_airports = IntermediateAirport.query.filter(IntermediateAirport.flight_id == flight_id).all()
    # Trả về kết quả dưới dạng danh sách dictionary
    return [intermediate_airport.to_dict() for intermediate_airport in intermediate_airports]

def find_airport(kw):
    airport_ids = [airport_id[0] for airport_id in Airport.query.filter(Airport.name.contains(kw)).with_entities(Airport.id).all()]
    return airport_ids
    
def load_aircarfts():
    return Aircraft.query.all()