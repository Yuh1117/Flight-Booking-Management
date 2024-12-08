from .models import Route, Flight, Airport, IntermediateAirport , db
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
    
def load_routes(kw=None, page=None):
    query = Route.query
    if kw:
        query = query.filter(Route.name.contains(kw))
    
    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    query = query.slice(start, start + page_size)
    
    return query.all()

def count_routes(kw=None):
    if kw:
        return Route.query.filter(Route.name.contains(kw)).count()
        
    return Route.query.count()

def get_route_by_id(id):
    return Route.query.get(id)
    

def find_intermediate_airport(flight_id):
    # Tìm tất cả sân bay trung gian của một chuyến bay cụ thể
    intermediate_airports = IntermediateAirport.query.filter(IntermediateAirport.flight_id == flight_id).all()
    # Trả về kết quả dưới dạng danh sách dictionary
    return [intermediate_airport.to_dict() for intermediate_airport in intermediate_airports]
