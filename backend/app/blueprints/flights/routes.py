from flask import render_template, jsonify, request, redirect, flash, url_for
from datetime import datetime as dt
from datetime import timedelta


from app import app, db
from . import flights_bp
from app.blueprints.auth import decorators
from . import dao
from .forms import FlightSchedulingForm


@flights_bp.route("/api/airlines", methods=["GET"])
def get_airlines():
    return jsonify([airline.to_dict() for airline in dao.get_airlines()])


@flights_bp.route("/api/seatclasses", methods=["GET"])
def get_seatclasses():
    return jsonify([seatclass.to_dict() for seatclass in dao.get_seat_classes()])


@flights_bp.route("/api/airports")
def get_airports():
    return jsonify([airport.to_dict() for airport in dao.get_airports()])


@flights_bp.route("/api/routes")
def get_routes():
    return jsonify([route.to_dict() for route in dao.get_routes()])


@flights_bp.route("/api/countries")
def get_countries():
    return jsonify([country.to_dict() for country in dao.get_countries()])


@flights_bp.route("/api/aircrafts")
def get_aircrafts():
    return jsonify([aircraft.to_dict() for aircraft in dao.get_aircrafts()])


def to_datetime(datetime_str):
    return dt.strptime(datetime_str, "%Y-%m-%dT%H:%M")


def validate_stopover_form():
    data = request.form.copy()

    # Get number of stopovers
    stopover_count = data.get("stopovers_num", type=int)

    if stopover_count <= 0:
        return True

    if stopover_count > dao.get_max_stopover_airports():
        flash("Number of stopovers is too large", "danger")
        return False

    # Check if the stopover info is provided
    for i in range(1, stopover_count + 1):
        if (
            not data.get(f"stopover_airport_{i}")
            or not data.get(f"stopover_arrival_time_{i}")
            or not data.get(f"stopover_departure_time_{i}")
        ):
            flash(f"Stopover {i} info is not provided fully!", "danger")
            return False

    # Check if the airports are unique
    stopover_airports = [
        data.get(f"stopover_airport_{i}", type=int)
        for i in range(1, stopover_count + 1)
    ]
    if len(stopover_airports) != len(set(stopover_airports)):
        flash("Stopover airports must be unique", "danger")
        return False
    if (
        data.get("departure_airport", type=int) in stopover_airports
        or data.get("arrival_airport", type=int) in stopover_airports
    ):
        flash(
            "Departure and arrival airports must be different from stopover airports",
            "danger",
        )
        return False

    # Check if the stopover times are valid
    departure_time = data.get("departure_time", type=to_datetime)
    arrival_time = data.get("arrival_time", type=to_datetime)
    latest_departure_time = (
        departure_time  # The latest departure time of the previous stopover
    )
    for i in range(1, stopover_count + 1):
        s_arrival_time = data.get(f"stopover_arrival_time_{i}", type=to_datetime)
        s_departure_time = data.get(f"stopover_departure_time_{i}", type=to_datetime)
        # The stopover must be between departure and arrival time
        if (
            s_departure_time <= s_arrival_time
            or s_arrival_time <= departure_time
            or s_departure_time >= arrival_time
        ):
            flash(f"Stopover {i} arrival time is invalid", "danger")
            return False
        # The stopover must be in order
        if s_arrival_time <= latest_departure_time:
            flash(f"Stopover {i} doesn't be in order!", "danger")
            return False
        latest_departure_time = s_departure_time

    return True


@flights_bp.route("/schedule", methods=["GET", "POST"])
@decorators.admin_or_flight_manager_required
def show_routes():
    form = FlightSchedulingForm()
    airports = dao.get_airports()
    form.departure_airport.choices = [(airport.id, airport) for airport in airports]
    form.arrival_airport.choices = [(airport.id, airport) for airport in airports]
    form.aircraft.choices = [
        (aircraft.id, aircraft) for aircraft in dao.get_aircrafts()
    ]
    max_stopover_airports = dao.get_max_stopover_airports()
    if form.validate_on_submit():
        if not validate_stopover_form():
            return redirect(request.referrer)

        departure_airport = int(form.departure_airport.data)
        arrival_airport = int(form.arrival_airport.data)
        aircraft = dao.get_aircraft_by_id(int(form.aircraft.data))
        departure_time = form.departure_time.data
        arrival_time = form.arrival_time.data
        code = form.flight_code.data

        # Get the route if the route doesn't exist, create a new one
        route = dao.get_route_by_airports(departure_airport, arrival_airport)
        if not route:
            route = dao.add_route(departure_airport, arrival_airport)

        # Add the flight
        flight = dao.add_flight(
            route.id, code, departure_time, arrival_time, aircraft.id
        )
        # Add the stopovers
        stopover_count = request.form.get("stopovers_num", type=int)
        for i in range(1, stopover_count + 1):
            stopover_airport = request.form.get(f"stopover_airport_{i}", type=int)
            stopover_arrival_time = request.form.get(
                f"stopover_arrival_time_{i}", type=to_datetime
            )
            stopover_departure_time = request.form.get(
                f"stopover_departure_time_{i}", type=to_datetime
            )
            dao.add_stopover(
                airport_id=stopover_airport,
                flight_id=flight.id,
                arrival_time=stopover_arrival_time,
                departure_time=stopover_departure_time,
                order=i,
                note=request.form.get(f"stopover_note_{i}", None),
            )

        flash("Flight scheduled successfully! Please provide flight prices.", "success")
        return redirect(url_for("flights.set_prices", id=flight.id))

    return render_template(
        "flights/schedule.html", form=form, max_stopover_airports=max_stopover_airports
    )


@flights_bp.route("/schedule/<id>/prices", methods=["GET", "POST"])
@decorators.admin_or_flight_manager_required
def set_prices(id):
    flight = dao.get_flight_by_id(id)
    if not flight or flight.seats:
        flash("Flight not found!", "info")
        return redirect("/")

    if request.method == "POST":
        data = request.form.deepcopy()

        # Get the prices
        prices = {}
        for seatclass in dao.get_seat_classes():
            if f"price_class_{seatclass.id}" in data.to_dict():
                prices[seatclass.id] = data.get(
                    f"price_class_{seatclass.id}", type=float
                )

        # Add flight seats
        for aircraft_seat in data.getlist("seat_ids", type=int):
            seat = dao.get_aircraft_seat_by_id(aircraft_seat)
            # Check if the seat exists and belongs to the aircraft
            if not seat or seat.aircraft_id != flight.aircraft_id:
                flash(f"Seat {aircraft_seat} not found!", "info")
                continue

            price = prices.get(seat.seat_class_id, None)

            dao.add_flight_seat(flight.id, seat.id, price)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash("Error setting prices!", "danger")
            return redirect(request.referrer)
        flash("Flight prices set successfully!", "success")
        return redirect(url_for("flights.showFlight", id=flight.id))
    return render_template("flights/create_flight_seats.html", flight=flight)


def to_date(date_str):
    return dt.strptime(date_str, "%Y-%m-%d").date()


@flights_bp.route("/search", methods=["GET"])
def searchFlights():
    # Get params from request
    departure_airport_id = request.args.get("from", type=int)
    arrival_airport_id = request.args.get("to", type=int)
    depart_date = request.args.get("depart", type=to_date)

    if not all([departure_airport_id, arrival_airport_id, depart_date]):
        # If user first access the page, return the plain search page
        return render_template("flights/search.html")

    # Get the route
    route = dao.get_route_by_airports(departure_airport_id, arrival_airport_id)
    if not route:
        # If the route does not exist, return an error message
        flash("This route doesn't exist!", "warning")
        return render_template("flights/search.html")

    # Get flights for the route
    page = request.args.get("page", default=1, type=int)
    flights = dao.get_flights_by_route_and_date(route.id, depart_date, page)

    if not flights:
        # If there are no flights for the route, return an error message
        flash("Couldn't find any flights for this route!", "info")
        return render_template(
            "flights/search.html", route=route, depart_date=depart_date
        )

    return render_template(
        "flights/search.html",
        route=route,
        flights=flights,
        depart_date=depart_date,
        search_time=dt.now(),
        staff_min_booking_time=dao.get_staff_min_booking_time(),
        customer_min_booking_time=dao.get_customer_min_booking_time(),
    )


@flights_bp.route("/flight/<id>", methods=["GET"])
def showFlight(id):
    flight = dao.get_flight_by_id(id)
    if not flight:
        flash("Flight not found!", "info")
        return redirect("/")
    return render_template(
        "flights/details.html",
        flight=flight,
        search_time=dt.now(),
        staff_min_booking_time=dao.get_staff_min_booking_time(),
        customer_min_booking_time=dao.get_customer_min_booking_time(),
        title="Flight Details",
    )
