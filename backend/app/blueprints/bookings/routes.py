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
    
    data = {
        "from": from_city,
        "to": to_city,
        "departDate": depart_date
    }
    
    # Giả sử `find_route_with_data` trả về kết quả với một danh sách các chuyến bay.
    result = find_route_with_data(data)
    
    if result["success"]:
        # Đảm bảo rằng chúng ta có danh sách các chuyến bay
        flights = result["flights"]
        
        # Sử dụng tham số `page` từ query string để phân trang
        page = request.args.get('page', 1, type=int)
        per_page = 5
        total_flights = len(flights)
        total_pages = ceil(total_flights / per_page)
        
        # Cắt chuyến bay dựa trên trang hiện tại
        flights_paginated = flights[(page - 1) * per_page: page * per_page]
        
        # Tạo dữ liệu phân trang
        pagination = {
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }
        
        return render_template(
            "main/booking.html",
            route=result["route"],
            flights=flights_paginated,
            intermediate_airport=result["intermediate_airport"],
            dataAirport=dataAirport,
            pagination=pagination, 
            data=data  # Truyền dữ liệu tìm kiếm vào template
        )
    
    return render_template("main/booking.html", dataAirport=dataAirport)




    
    




