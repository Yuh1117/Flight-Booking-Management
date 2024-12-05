from flask import render_template, jsonify, request
from flask_login import login_required
from . import bookings_bp, models
from ..flights.models import Airport, Route, Flight
from app import app


@bookings_bp.route("/booking")
@login_required
def booking():
    """Render the about page."""
    return render_template("main/booking.html")


# API để lấy danh sách airport
@app.route("/api/airports", methods=["GET"])
def get_airports():
    airports = Airport.query.all()
    airport_list = [
        {"id": airport.id, "name": airport.name, "code": airport.code}
        for airport in airports
    ]
    return jsonify(airport_list)


@app.route("/find_route", methods=["POST"])
def find_route():
    try:
        # Lấy dữ liệu JSON từ request
        data = request.get_json()
        print(data)
        if not data:
            return (
                jsonify(
                    {"success": False, "message": "Dữ liệu không hợp lệ hoặc bị thiếu"}
                ),
                400,
            )

        # Ép kiểu từ và đến thành số nguyên
        try:
            from_value = int(data.get("from"))
            to_value = int(data.get("to"))
        except (ValueError, TypeError):
            return (
                jsonify(
                    {"success": False, "message": "From và To phải là số nguyên hợp lệ"}
                ),
                400,
            )

        # Truy vấn tuyến đường
        route = Route.query.filter_by(
            depart_airport_id=from_value, arrive_airport_id=to_value
        ).first()
        if route:
            print(route.to_dict())

            # Truy vấn các chuyến bay theo route_id
            flights = route.flights

            if flights:
                flights_data = [flight.to_dict() for flight in flights]
                print(flights_data)
                return jsonify(
                    {"success": True, "route": route.to_dict(), "flights": flights_data}
                )
            else:
                return jsonify(
                    {"success": True, "route": route.to_dict(), "flights": []}
                )
        else:
            return (
                jsonify({"success": False, "message": "Không tìm thấy tuyến đường"}),
                404,
            )
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi hệ thống: {str(e)}"}), 500
