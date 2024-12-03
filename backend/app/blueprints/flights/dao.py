from .models import Route, db

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