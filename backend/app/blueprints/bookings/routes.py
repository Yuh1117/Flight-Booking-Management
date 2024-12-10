from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from . import bookings_bp, models
from ..flights.models import Airport, Route, Flight
from app.blueprints.bookings.models import Reservation
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
        "depart": depart_date
    }
    page = int(request.args.get("page", 1))
    result = find_route_with_data(data, page=page)
    page_size = app.config['PAGE_SIZE']
    total_flights = result.get("total_flights", 0)  
    total_pages = (total_flights + page_size - 1) // page_size  
    if result["success"]:
        flights = result["flights"]
        return render_template(
            "bookings/index.html",
            route=result["route"],
            flights=flights,
            intermediate_airport=result["intermediate_airport"],
            dataAirport=dataAirport,
            data=data, 
            current_page=page,
            total_pages=total_pages
        )
    return render_template("bookings/index.html", dataAirport=dataAirport, current_page=page)

    
    
@bookings_bp.route("/booking/reserve", methods=["GET"])
@login_required
def reserve_ticket():
    flight_id = request.args.get("flight_id")
    ticket_class = request.args.get("ticket_class")
    flight = Flight.query.get(flight_id)
    flight_seats = flight.flight_seats
    user = current_user
    if not flight:
        return "Chuyến bay không tồn tại!", 404
    return render_template(
        "bookings/detail.html", 
        flight=flight, 
        ticket_class=ticket_class, 
        flight_seats=flight_seats,
        user=user
        )

    





