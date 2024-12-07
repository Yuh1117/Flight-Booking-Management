from . import flights_bp, models
from app.blueprints.auth import decorators
from flask import render_template, jsonify, request
from flask_login import current_user

@flights_bp.route("/schedule", methods=['get', 'post'])
@decorators.flight_manager_required
def show_routes():
    if request.method.__eq__('GET'):
        return render_template("flights/show.html")
    
@flights_bp.route("/schedule/<id>", methods=['get'])
@decorators.flight_manager_required
def schedule(id):
    return render_template("flights/schedule.html", id=id)

