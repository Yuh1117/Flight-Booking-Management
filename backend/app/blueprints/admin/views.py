from flask import redirect, url_for, request
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from app.blueprints.auth.models import UserRole
from flask_admin import Admin, AdminIndexView, BaseView
from app import app, db


from app.blueprints.auth.models import User
from app.blueprints.flights.models import Route
from app.blueprints.flights.models import Flight
from app.blueprints.flights.models import Airport
from app.blueprints.flights.models import Aircraft
from app.blueprints.flights.models import Country
from app.blueprints.flights.models import Flight
from app.blueprints.flights.models import Airline


class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class AdminView(AuthenticatedView):
    def is_accessible(self):
        return super().is_accessible() and current_user.role == UserRole.ADMIN


class MyAdminView(AdminIndexView, AdminView):
    pass

class UserView(ModelView, AdminView):
    pass


class RouteAdmin(ModelView):
    column_list = ('id', 'depart_airport_name', 'arrive_airport_name')

    column_labels = {
        'depart_airport_name': 'Depart Airport',
        'arrive_airport_name': 'Arrive Airport'
    }
class AirportAdmin(ModelView):
    column_list = ('id', 'name', 'code', 'country_name')

    column_labels = {
        'country_name': 'Country'
    }
class AircraftAdmin(ModelView):
    # Hiển thị thêm airline_name
    column_list = ("id", "name",  "airline_name")
    column_labels = {
        "id": "ID",
        "name": "Tên Máy Bay",
        "airline_name": "Hãng Hàng Không"
    }
class AirlineAdmin(ModelView):
    column_list = ("id", "name")

    column_labels = {
        "id": "ID",
        "name": "Tên Hãng"
    }    
admin = Admin(app, name="Admin", template_mode="bootstrap4", index_view=MyAdminView())
admin.add_view(UserView(User, db.session, name="Users"))
admin.add_view(RouteAdmin(Route, db.session, name="Routes"))
admin.add_view(UserView(Flight, db.session, name="Flights"))
admin.add_view(AirportAdmin(Airport, db.session, name="Airports"))
admin.add_view(UserView(Country, db.session, name="Countries"))
admin.add_view(AircraftAdmin(Aircraft, db.session, name="Aircrafts"))
admin.add_view(AirlineAdmin(Airline, db.session, name="Airlines"))
