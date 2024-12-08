from . import flights_bp, models
from app.blueprints.auth import decorators
from flask import render_template, jsonify, request, redirect
from flask_login import current_user
from . import dao
import math
from app import app

@flights_bp.route("/schedule", methods=['GET', 'POST'])
@decorators.flight_manager_required
def show_routes():
    if request.method.__eq__('GET'):
        kw_depart_airport = request.args.get('kw_depart_airport')
        kw_arrive_airport = request.args.get('kw_arrive_airport')
        page = request.args.get('page', 1)
        
        airports = dao.load_stopover_airport()
        
        routes = dao.load_routes(kw_depart_airport=kw_depart_airport, kw_arrive_airport=kw_arrive_airport, page=int(page))
        total_elements = dao.count_routes(kw_depart_airport, kw_arrive_airport)
        
        if kw_arrive_airport or kw_depart_airport:
            query_string = f"&kw_depart_airport={kw_depart_airport}&kw_arrive_airport={kw_arrive_airport}"
        else:
            query_string = ''
    
        return render_template("flights/show.html", routes=routes, pages=math.ceil(total_elements / app.config['PAGE_SIZE']),
                               current_page=int(page), kw_depart_airport=kw_depart_airport if kw_depart_airport else '',
                               kw_arrive_airport=kw_arrive_airport if kw_arrive_airport else '', airports=airports, query_string=query_string)
    
    if request.method.__eq__('POST'):
        data = request.form.copy()
        print(data)
       
        return redirect(f'/schedule/{data['route_id']}')

@flights_bp.route("/schedule/<id>", methods=['get'])
@decorators.flight_manager_required
def schedule(id):
    route = dao.get_route_by_id(id)
    page = request.args.get('page')
    if page:
        flights = dao.load_flights(page=int(page))
        total_elements = dao.count_flights()
    else:
        flights = None
        total_elements = None
        
    aircrafts = dao.load_aircarfts()
            
    # not stopover airport
    airports = dao.load_stopover_airport()
    
    
    return render_template("flights/schedule.html", id=id, route=route, airports=airports, flights=flights, current_page=int(page) if page else '',
                           pages=math.ceil(total_elements / app.config['PAGE_SIZE']) if total_elements else '', aircrafts=aircrafts)

