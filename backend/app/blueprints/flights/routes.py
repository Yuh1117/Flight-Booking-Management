from . import flights_bp, models
from app.blueprints.auth import decorators
from flask import render_template, jsonify, request, redirect, flash
from flask_login import current_user
from . import dao
import math
from app import app
from datetime import datetime, timedelta

@flights_bp.route("/schedule", methods=['GET'])
@decorators.flight_manager_required
def show_routes():
    kw_depart_airport = request.args.get('kw_depart_airport')
    kw_arrive_airport = request.args.get('kw_arrive_airport')
    page = request.args.get('page', 1)
    
    airports = dao.load_airports()
    
    routes = dao.load_routes(kw_depart_airport=kw_depart_airport, kw_arrive_airport=kw_arrive_airport, page=int(page))
    total_elements = dao.count_routes(kw_depart_airport, kw_arrive_airport)
    
    if kw_arrive_airport or kw_depart_airport:
        query_string = f"&kw_depart_airport={kw_depart_airport}&kw_arrive_airport={kw_arrive_airport}"
    else:
        query_string = ''

    return render_template("flights/show.html", routes=routes, pages=math.ceil(total_elements / app.config['PAGE_SIZE']),
                            current_page=int(page), kw_depart_airport=kw_depart_airport if kw_depart_airport else '',
                            kw_arrive_airport=kw_arrive_airport if kw_arrive_airport else '', airports=airports, query_string=query_string)


@flights_bp.route("/schedule/<id>", methods=['GET', 'POST'])
@decorators.flight_manager_required
def schedule(id):
    if request.method.__eq__('GET'):
        route = dao.get_route_by_id(id)
        page = request.args.get('page')
        if page:
            flights = dao.load_flights(page=int(page))
            total_elements = dao.count_flights()
        else:
            flights = None
            total_elements = None
            
        aircrafts = dao.load_aircarfts()
                
        airports = dao.load_airports(route.depart_airport_id, route.arrive_airport_id)
        
        
        return render_template("flights/schedule.html", route=route, airports=airports, flights=flights, current_page=int(page) if page else '',
                            pages=math.ceil(total_elements / app.config['PAGE_SIZE']) if total_elements else '', aircrafts=aircrafts)
    
    if request.method.__eq__('POST'):
        data = request.form.copy()
        # print(data)
        message = None

        # flight 
        depart_time = datetime.strptime(data['departureDateTime'],  "%Y-%m-%dT%H:%M")
        time_to_add = timedelta(minutes=int(data['flightDuration']))
        arrive_time = depart_time + time_to_add
        aircraft_id = data['aircraft']
        
        # intermediate airport
        intermediate_airport = data.getlist('intermediateAirport')
        if intermediate_airport: 
            # intermediate time
            intermediate_arrive_time = data.getlist('intermediateArrivalTime')
            intermediate_duration = data.getlist('intermediateDuration')
            # intermediate note
            intermediate_notes = data.getlist('intermediateNotes')

            # add flight
            for t in intermediate_duration:
                arrive_time += timedelta(minutes=int(t))
            flight = dao.add_flight(route_id=data['route_id'], depart_time=depart_time, arrive_time=arrive_time, aircraft_id=aircraft_id)
            
            if flight:
                # add intermediate_airport
                for i in range(len(intermediate_airport)):
                    intermediate_arrive_time[i] = datetime.strptime(intermediate_arrive_time[i],  "%Y-%m-%dT%H:%M")
                    intermediate_depart_time = intermediate_arrive_time[i] + timedelta(minutes=int(intermediate_duration[i]))

                    dao.add_intermediate_airport(airport_id=intermediate_airport[i], flight_id=flight.id, arrival_time=intermediate_arrive_time[i],
                                                 departure_time=intermediate_depart_time, order=(i+1))

                message = 'Schedule success'
            else:
                message = 'Schedule fail'

        else:
            if(dao.add_flight(route_id=data['route_id'], depart_time=depart_time, arrive_time=arrive_time, aircraft_id=aircraft_id)):
                message = 'Schedule success'
            else:
                message = 'Schedule fail'
        
        flash(message)
        return redirect(f'/schedule/{data['route_id']}')

