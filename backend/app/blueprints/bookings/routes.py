from flask import render_template, jsonify, request
from flask_login import login_required
from . import bookings_bp, models
from ..flights.models import Airport, Route, Flight
from ..flights.dao import find_intermediate_airport
from app import app
from datetime import datetime
from .dao import find_route_with_data, get_airports
from math import ceil


@bookings_bp.route("/booking")
def booking():
    dataAirport = get_airports()
    from_city = request.args.get('from')     
    to_city = request.args.get('to')        
    depart_date = request.args.get('depart') 
    print(depart_date)
    
    # Truyền dữ liệu tìm kiếm
    data = {
        "from": from_city,
        "to": to_city,
        "depart": depart_date
    }

    # Lấy trang hiện tại từ URL hoặc mặc định là 1
    page = int(request.args.get("page", 1))

    # Gọi hàm tìm kiếm chuyến bay với dữ liệu và trang hiện tại
    result = find_route_with_data(data, page=page)
    
    # Xử lý kết quả tìm kiếm
    page_size = app.config['PAGE_SIZE']
    total_flights = result.get("total_flights", 0)  # Lấy tổng số chuyến bay
    total_pages = (total_flights + page_size - 1) // page_size  # Tính số trang

    # Nếu tìm thấy chuyến bay, render template
    if result["success"]:
        flights = result["flights"]
        return render_template(
            "main/booking.html",
            route=result["route"],
            flights=flights,
            intermediate_airport=result["intermediate_airport"],
            dataAirport=dataAirport,
            data=data,  # Truyền dữ liệu tìm kiếm vào template
            current_page=page,
            total_pages=total_pages
        )

    # Nếu không có chuyến bay, render trang trống
    return render_template("main/booking.html", dataAirport=dataAirport, current_page=page)




    
    




