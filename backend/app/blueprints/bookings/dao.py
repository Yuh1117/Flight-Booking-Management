from ..flights.models import Airport, Route, Flight, IntermediateAirport
from app import app
from datetime import datetime

def get_airports():
    airports = Airport.query.all()
    return [
        {"id": airport.id, "name": airport.name, "code": airport.code}
        for airport in airports
    ]  
def get_routes():
    routes = Route.query.all()
    return [
        {"id": route.id, "depart_airport_id": route.depart_airport_id,
         "arrive_airport_id": route.arrive_airport_id, "departure_airport": route.depart_airport.name,
         "arrive_airport": route.arrive_airport.name}
        for route in routes
    ]

def get_route(from_value, to_value):
    """Truy vấn tuyến đường theo sân bay đi và đến."""
    return Route.query.filter_by(
        depart_airport_id=from_value, 
        arrive_airport_id=to_value
    ).first()

def get_flights_by_route(route_id, depart_date):
    """Truy vấn các chuyến bay theo route_id và ngày khởi hành."""
    return Flight.query.filter(
        Flight.route_id == route_id,
        Flight.depart_time >= datetime.combine(depart_date, datetime.min.time()),
        Flight.depart_time < datetime.combine(depart_date, datetime.max.time())
    ).all()

def get_intermediate_airports(flights):
    """Truy vấn danh sách các sân bay trung gian liên quan đến chuyến bay."""
    intermediate_airports = []
    for flight in flights:
        intermediate_airport_list = IntermediateAirport.query.filter(
            IntermediateAirport.flight_id == flight.id
        ).all()
        for intermediate_airport in intermediate_airport_list:
            intermediate_airports.append(intermediate_airport)
    return intermediate_airports

def paginate_results(results, page, page_size):
    """Phân trang kết quả."""
    start = (page - 1) * page_size
    end = start + page_size
    return results[start:end]

def find_route_with_data(data, page):
    """Hàm chính xử lý yêu cầu."""
    try:
        from_value = int(data.get("from"))
        to_value = int(data.get("to"))
        depart_date_str = data.get("depart")
        depart_date = datetime.strptime(depart_date_str, "%Y-%m-%d").date()
        # Truy vấn tuyến đường
        route = get_route(from_value, to_value)
        if not route:
            return {"success": False, "message": "Không tìm thấy tuyến đường"}
        # Truy vấn chuyến bay
        flights = get_flights_by_route(route.id, depart_date)
        if not flights:
            return {"success": True, "message": "Không tìm thấy chuyến bay nào", "flights": []}
        # Truy vấn sân bay trung gian
        intermediate_airports = get_intermediate_airports(flights)
        # Phân trang dữ liệu chuyến bay
        page_size = app.config.get("PAGE_SIZE", 10)
        flights_data = paginate_results([flight.to_dict() for flight in flights], page, page_size)
        return {
            "success": True,
            "flights": flights_data,
            "route": route,
            "intermediate_airports": intermediate_airports,
            "total_flights": len(flights),
        }
    except Exception as e:
        return {"success": False, "message": f"Lỗi hệ thống: {str(e)}"}

