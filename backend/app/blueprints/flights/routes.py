from . import flights_bp, models
from app.blueprints.auth import decorators
from flask import render_template, jsonify, request
from flask_login import current_user
from . import dao
import math
from app import app

@flights_bp.route("/schedule", methods=['GET', 'POST'])
@decorators.flight_manager_required
def show_routes():
    if request.method.__eq__('GET'):
        kw = request.args.get('kw')
        page = request.args.get('page', 1)
        
        routes = dao.load_routes(kw=kw, page=int(page))
        total_elements = dao.count_routes(kw)
    
        return render_template("flights/show.html", routes=routes, pages=math.ceil(total_elements / app.config['PAGE_SIZE']),
                               current_page=int(page), kw=kw if kw != None else '')

@flights_bp.route("/schedule/<id>", methods=['get'])
@decorators.flight_manager_required
def schedule(id):
    route = dao.get_route_by_id(id)
    return render_template("flights/schedule.html", id=id, route=route)

