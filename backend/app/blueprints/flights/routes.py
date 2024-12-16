from flask import render_template, jsonify, request, redirect, flash
from datetime import datetime, timedelta
import math


from . import flights_bp
from app.blueprints.auth import decorators
from app.blueprints.auth.models import UserRole
from flask_login import current_user
from . import dao
from app import app


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


@flights_bp.route("/schedule", methods=["GET"])
@decorators.flight_manager_required
def show_routes():
    kw_depart_airport = request.args.get("kw_depart_airport")
    kw_arrive_airport = request.args.get("kw_arrive_airport")
    page = request.args.get("page", 1)

    airports = dao.load_airports()

    routes = dao.load_routes(
        kw_depart_airport=kw_depart_airport,
        kw_arrive_airport=kw_arrive_airport,
        page=int(page),
    )
    total_elements = dao.count_routes(kw_depart_airport, kw_arrive_airport)

    if kw_arrive_airport or kw_depart_airport:
        query_string = f"&kw_depart_airport={kw_depart_airport}&kw_arrive_airport={kw_arrive_airport}"
    else:
        query_string = ""

    return render_template(
        "flights/show.html",
        routes=routes,
        pages=math.ceil(total_elements / app.config["PAGE_SIZE"]),
        current_page=int(page),
        kw_depart_airport=int(kw_depart_airport) if kw_depart_airport else "",
        kw_arrive_airport=int(kw_arrive_airport) if kw_arrive_airport else "",
        airports=airports,
        query_string=query_string,
    )


@flights_bp.route("/schedule/<id>", methods=["GET", "POST"])
@decorators.flight_manager_required
def schedule(id):
    if request.method.__eq__("GET"):
        route = dao.get_route_by_id(id)
        page = request.args.get("page")
        if page:
            flights = dao.load_flights(page=int(page))
            total_elements = dao.count_flights()
        else:
            flights = None
            total_elements = None

        aircrafts = dao.load_aircarfts()

        airports = dao.load_airports(route.depart_airport_id, route.arrive_airport_id)

        # regulation
        max_stopover_airports = dao.get_max_stopover_airports()
        min_flight_duration = dao.get_min_flight_duration()
        max_flight_duration = dao.get_max_flight_duration()

        regulations = {
            "max_stopover_airports": max_stopover_airports,
            "min_flight_duration": min_flight_duration,
            "max_flight_duration": max_flight_duration,
        }

        return render_template(
            "flights/schedule.html",
            route=route,
            airports=airports,
            flights=flights,
            current_page=int(page) if page else "",
            pages=(
                math.ceil(total_elements / app.config["PAGE_SIZE"])
                if total_elements
                else ""
            ),
            aircrafts=aircrafts,
            regulations=regulations,
        )

    if request.method.__eq__("POST"):
        data = request.form.copy()
        # print(data)
        message = None

        # flight
        depart_time = datetime.strptime(data["departureDateTime"], "%Y-%m-%dT%H:%M")
        time_to_add = timedelta(minutes=int(data["flightDuration"]))
        arrive_time = depart_time + time_to_add
        aircraft_id = data["aircraft"]

        # intermediate airport
        intermediate_airport = data.getlist("intermediateAirport")
        if intermediate_airport:
            # intermediate time
            intermediate_arrive_time = data.getlist("intermediateArrivalTime")
            intermediate_duration = data.getlist("intermediateDuration")
            # intermediate note
            intermediate_notes = data.getlist("intermediateNotes")

            # add flight
            for t in intermediate_duration:
                arrive_time += timedelta(minutes=int(t))
            flight = dao.add_flight(
                route_id=data["route_id"],
                depart_time=depart_time,
                arrive_time=arrive_time,
                aircraft_id=aircraft_id,
            )

            if flight:
                # add intermediate_airport
                for i in range(len(intermediate_airport)):
                    intermediate_arrive_time[i] = datetime.strptime(
                        intermediate_arrive_time[i], "%Y-%m-%dT%H:%M"
                    )
                    intermediate_depart_time = intermediate_arrive_time[i] + timedelta(
                        minutes=int(intermediate_duration[i])
                    )

                    dao.add_intermediate_airport(
                        airport_id=intermediate_airport[i],
                        flight_id=flight.id,
                        arrival_time=intermediate_arrive_time[i],
                        departure_time=intermediate_depart_time,
                        order=(i + 1),
                    )

                message = "Schedule success"
            else:
                message = "Schedule fail"

        else:
            if dao.add_flight(
                route_id=data["route_id"],
                depart_time=depart_time,
                arrive_time=arrive_time,
                aircraft_id=aircraft_id,
            ):
                message = "Schedule success"
            else:
                message = "Schedule fail"

        flash(message)
        return redirect(f"/schedule/{data['route_id']}")


# @flights_bp.route("/api/schedule/validate", methods=['POST'])
# @decorators.flight_manager_required
# def validate():
#     data = request.json
#     message = {
#         "flight_duration":'',

#     }
#     max_flight_duration = dao.get_max_flight_duration()
#     min_flight_duration = dao.get_min_flight_duration()

#     if(int(data.get('flightDuration')) < min_flight_duration or int(data.get('flightDuration')) > max_flight_duration):
#         message['flight_duration'] = f"Flight duration must be between {min_flight_duration} - {max_flight_duration} minutes!"

#     return jsonify(message)


def paginate_results(results, page, page_size):
    start = (page - 1) * page_size
    end = start + page_size
    return results[start:end]


@flights_bp.route("/search", methods=["GET"])
def searchFlights():
    # Get params from request
    departure_airport_id = request.args.get("from", type=int)
    arrival_airport_id = request.args.get("to", type=int)
    depart_date_str = request.args.get("depart")

    if not all([departure_airport_id, arrival_airport_id, depart_date_str]):
        # If user first access the page, return the plain search page
        return render_template("flights/search.html")
    try:
        # Check if the date is in the correct format
        depart_date = datetime.strptime(depart_date_str, "%Y-%m-%d").date()
    except ValueError:
        # If the date is not in the correct format, return an error message
        flash("Invalid date format!", "info")
        return render_template("flights/search.html")

    # Get the route
    route = dao.get_route_by_airports(departure_airport_id, arrival_airport_id)
    if not route:
        # If the route does not exist, return an error message
        flash("Couldn't find any flights for this route!", "info")
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
        search_time=datetime.now(),
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
        search_time=datetime.now(),
        staff_min_booking_time=dao.get_staff_min_booking_time(),
        customer_min_booking_time=dao.get_customer_min_booking_time(),
        title="Flight Details",
    )
