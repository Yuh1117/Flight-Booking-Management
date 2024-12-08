from ..flights.models import Airport, Route, Flight, IntermediateAirport
from ..flights.dao import find_intermediate_airport
from app import app
from datetime import datetime

def get_airports():
    airports = Airport.query.all()
    return [
        {"id": airport.id, "name": airport.name, "code": airport.code}
        for airport in airports
    ]  



def find_route_with_data(data):
    try:
        print("Yêu cầu truyền vào", data)
        if not data:
            return {"success": False, "message": "Dữ liệu không hợp lệ hoặc bị thiếu"}
        # Ép kiểu từ và đến thành số nguyên
        try:
            from_value = int(data.get("from"))
            to_value = int(data.get("to"))
        except (ValueError, TypeError):
            return {"success": False, "message": "From và To phải là số nguyên hợp lệ"}
        # Lấy ngày khởi hành từ dữ liệu
        depart_date_str = data.get('departDate')
        if not depart_date_str:
            return {"success": False, "message": "Ngày khởi hành (departDate) không được cung cấp"}

        try:
            # Chuyển đổi ngày khởi hành sang định dạng datetime
            depart_date = datetime.strptime(depart_date_str, "%Y-%m-%d").date()
        except ValueError:
            return {"success": False, "message": "Ngày khởi hành (departDate) không hợp lệ. Định dạng đúng: YYYY-MM-DD"}
        # Truy vấn tuyến đường
        route = Route.query.filter_by(
            depart_airport_id=from_value, arrive_airport_id=to_value
        ).first()

        if route:
            # Truy vấn các chuyến bay theo route_id và lọc ngày khởi hành
            flights = Flight.query.filter(
                Flight.route_id == route.id,
                Flight.depart_time >= datetime.combine(depart_date, datetime.min.time()),
                Flight.depart_time < datetime.combine(depart_date, datetime.max.time())
            ).all()
            # Lấy danh sách tất cả sân bay trung gian
            # Danh sách lưu tất cả sân bay trung gian dưới dạng dictionary
            intermediate_airports = []

            # Duyệt qua danh sách các chuyến bay
            for flight in flights:
                # Thêm các sân bay trung gian của từng chuyến bay và chuyển chúng sang dictionary
                intermediate_airports.extend([airport.to_dict() for airport in flight.intermediate_airports])
                print("chuyến bay", flight.id)
                for intermediate_airport in flight.intermediate_airports:
                        print(intermediate_airport)
                        print(intermediate_airport.airport.name)  # Giả sử 'name' là thuộc tính của 'Airport'
                        print("==========")

            # In danh sách dictionary



            flights_data = [flight.to_dict() for flight in flights]
            print("flight data", flights_data)
            print("stops data", intermediate_airports)
            return {
                "success": True,
                "route": route.to_dict(),
                "flights": flights_data,
                "intermediate_airport": intermediate_airports,
            }
        else:
            return {"success": False, "message": "Không tìm thấy tuyến đường"}
    except Exception as e:
        return {"success": False, "message": f"Lỗi hệ thống: {str(e)}"}
