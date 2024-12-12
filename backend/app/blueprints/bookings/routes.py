from flask import  request, render_template, redirect, url_for,jsonify
from flask_login import login_required, current_user
from . import bookings_bp, models
from ..flights.models import Airport, Route, Flight, FlightSeat
from app.blueprints.bookings.models import Reservation
from app import app,db
from datetime import datetime
from .dao import find_route_with_data, get_airports, get_routes
from .models import Reservation, ReservationStatus
from datetime import datetime
from math import ceil


@app.route("/api/airports") 
def api_airports(): 
    return jsonify(get_airports())
@app.route("/api/routes") 
def api_routes(): 
    return jsonify(get_routes())


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
    result = find_route_with_data(data ,page)
    page_size = app.config['PAGE_SIZE']
    total_flights = result.get("total_flights", 0)  
    total_pages = (total_flights + page_size - 1) // page_size  

    if result["success"]:
        flights = result["flights"]
        return render_template(
            "bookings/index.html",
            route=result["route"],
            flights=flights,
            intermediate_airports=result["intermediate_airports"],
            dataAirport=dataAirport,
            data=data, 
            current_page=page,
            total_pages=total_pages
        )
    return render_template("bookings/index.html", dataAirport=dataAirport, current_page=page)

    
    
@bookings_bp.route("/booking/reserve", methods=["GET", "POST"])
@login_required
def reserve_ticket():
    flight_id = request.args.get("flight_id")
    ticket_class = request.args.get("ticket_class")
    flight = Flight.query.get(flight_id)
    flight_seats = FlightSeat.query.filter_by(flight_id=flight_id).all()
    

    if request.method == "POST":
        # Lấy thông tin ghế đã chọn
        seat_id = request.form.get("seat_id")
        print(seat_id)
        seat = FlightSeat.query.get(seat_id)
        print(seat)
        reservation = Reservation(
            user_id=current_user.id,
            flight_seat_id=seat.id,
            status=ReservationStatus.UNPAID,
            created_at=datetime.now()
        )
        db.session.add(reservation)
        db.session.commit()
        print(reservation)
        return redirect(url_for("bookings.confirmation", reservation_id=reservation.id))
    return render_template("bookings/detail.html", flight=flight, ticket_class=ticket_class, flight_seats=flight_seats, user=current_user)

@bookings_bp.route("/booking/confirmation/<int:reservation_id>", methods=["GET"])
@login_required
def confirmation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    flight_seat = reservation.flight_seat
    flight = flight_seat.flight
    return render_template("bookings/confirmation.html", reservation=reservation, flight=flight, flight_seat=flight_seat)
