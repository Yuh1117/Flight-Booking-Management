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

@flights_bp.route("/api/aircraft_seats/<id>")
def get_aircraft_seates(id):
    return jsonify([aircraft_seat.to_dict() for aircraft_seat in dao.get_aircraft_seats_by_aircraft(id)])


@flights_bp.route("/schedule", methods=["GET"])
@decorators.admin_or_flight_manager_required
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
@decorators.admin_or_flight_manager_required
def schedule(id):
    if request.method.__eq__("GET"):
        route = dao.get_route_by_id(id)
        page = request.args.get("page")
        if page:
            flights = dao.load_flights(page=int(page), route_id=route.id)
            total_elements = dao.count_flights(route_id=route.id)
        else:
            flights = None
            total_elements = None

        aircrafts = dao.load_aircarfts()

        airports = dao.load_airports(route.depart_airport_id, route.arrive_airport_id)

        # regulation
        max_stopover_airports = dao.get_max_stopover_airports()

        regulations = {
            "max_stopover_airports": max_stopover_airports,
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
        
        #aircraft seat
        aircraft_seats_id = data.getlist("flightSeat")
        aircraft_seats_price = data.getlist("price")
        aircraft_seats_currency = data.getlist("currency")

        # stopover airport
        stopover_airport = data.getlist("stopoverAirport")
        if stopover_airport:
            # stopover time
            stopover_arrive_time = data.getlist("stopoverArrivalTime")
            stopover_duration = data.getlist("stopoverDuration")
            # stopover note
            stopover_notes = data.getlist("stopoverNotes")

            # add flight
            for t in stopover_duration:
                arrive_time += timedelta(minutes=int(t))
                
            flight = dao.add_flight(
                route_id=data["route_id"],
                depart_time=depart_time,
                arrive_time=arrive_time,
                aircraft_id=aircraft_id,
            )

            if flight:
                #add aircraft seat
                for i in range(len(aircraft_seats_id)):
                    dao.add_flight_seat(flight_id=flight.id, aircraft_seat_id=aircraft_seats_id[i],
                                        price=aircraft_seats_price[i], currency=aircraft_seats_currency[i])
                    
                # add stopover_airport
                for i in range(len(stopover_airport)):
                    stopover_arrive_time[i] = datetime.strptime(
                        stopover_arrive_time[i], "%Y-%m-%dT%H:%M"
                    )
                    stopover_depart_time = stopover_arrive_time[i] + timedelta(
                        minutes=int(stopover_duration[i])
                    )

                    dao.add_intermediate_airport(
                        airport_id=stopover_airport[i],
                        flight_id=flight.id,
                        arrival_time=stopover_arrive_time[i],
                        departure_time=stopover_depart_time,
                        order=(i + 1),
                    )

                message = "Schedule success"
            else:
                message = "Schedule fail"

        else:
            flight =  dao.add_flight(
                route_id=data["route_id"],
                depart_time=depart_time,
                arrive_time=arrive_time,
                aircraft_id=aircraft_id,
            )
            
            if flight:
                for i in range(len(aircraft_seats_id)):
                    dao.add_flight_seat(flight_id=flight.id, aircraft_seat_id=aircraft_seats_id[i],
                                        price=aircraft_seats_price[i], currency=aircraft_seats_currency[i])
                
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
    print(route.id)
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


@flights_bp.route("/api/schedule/validate", methods=["POST"])
@decorators.admin_or_flight_manager_required
def validate():
    data = request.json
    message = {
        "flight_duration": "",
        "depart_date_time": "",
        "stopover_airport": [],
        "stopover_duration": [],
        "stopover_arrival_time": [],
        "valid": False,
    }
    ##
    max_flight_duration = dao.get_max_flight_duration()
    min_flight_duration = dao.get_min_flight_duration()

    if (
        int(data.get("flightDuration")) < min_flight_duration
        or int(data.get("flightDuration")) > max_flight_duration
    ):
        message["flight_duration"] = (
            f"Flight duration must be between {min_flight_duration} - {max_flight_duration} minutes!"
        )

    ##
    now = datetime.strptime(str(datetime.now()), "%Y-%m-%d %H:%M:%S.%f")
    depart_date_time = datetime.strptime(
        data.get("departureDateTime"), "%Y-%m-%dT%H:%M"
    )

    if depart_date_time < now:
        message["depart_date_time"] = "Invalid date time"

    ##
    duplicate = []
    if data.get("stopoverAirport"):
        for i in range(0, len(data.get("stopoverAirport"))):
            message["stopover_airport"].append("")
            if i == 0:
                duplicate.append(data.get("stopoverAirport")[i])
                continue

            if data.get("stopoverAirport")[i] in duplicate:
                message["stopover_airport"][i] = "Duplicate Airport"
            duplicate.append(data.get("stopoverAirport")[i])

    ##
    min_stopover_duration = dao.get_min_stopover_duration()
    max_stopover_duration = dao.get_max_stopover_duration()

    if data.get("stopoverDuration"):
        for i in range(0, len(data.get("stopoverDuration"))):
            message["stopover_duration"].append("")
            if (
                int(data.get("stopoverDuration")[i]) < min_stopover_duration
                or int(data.get("stopoverDuration")[i]) > max_stopover_duration
            ):
                message["stopover_duration"][
                    i
                ] = f"Value must be between {min_stopover_duration} - {max_stopover_duration}"

    ##
    if data.get("stopoverArrivalTime"):
        for i in range(0, len(data.get("stopoverArrivalTime"))):
            message["stopover_arrival_time"].append("")
            stopover_arrival_time = datetime.strptime(
                data.get("stopoverArrivalTime")[i], "%Y-%m-%dT%H:%M"
            )
            if stopover_arrival_time < depart_date_time:
                message["stopover_arrival_time"][i] = "Invalid arrival time"

    ####
    stopover_airport_valid = all(
        item == "" for item in message["stopover_airport"]
    )
    stopover_duration_valid = all(
        item == "" for item in message["stopover_duration"]
    )
    stopover_arrival_time_valid = all(
        item == "" for item in message["stopover_arrival_time"]
    )
    if (
        message["depart_date_time"] == ""
        and message["flight_duration"] == ""
        and stopover_airport_valid
        and stopover_duration_valid
        and stopover_arrival_time_valid
    ):
        message["valid"] = True

    return jsonify(message)
