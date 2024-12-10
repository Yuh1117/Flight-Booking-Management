from flask import redirect, flash
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_admin import AdminIndexView, BaseView, Admin, expose
from wtforms.fields import IntegerField
from wtforms.validators import DataRequired
from wtforms.validators import NumberRange

from app import app, db
from app.blueprints.auth.models import User
from app.blueprints.auth.models import UserRole
from app.blueprints.auth.routes import logout_process
from app.blueprints.flights.models import *
from app.blueprints.flights import dao as flight_dao


class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class AdminView(AuthenticatedView):
    def is_accessible(self):
        return super().is_accessible() and current_user.role == UserRole.ADMIN


class MyAdminView(AdminIndexView, AdminView):
    pass


class CountryAdmin(ModelView, AdminView):
    column_list = ("id", "name", "code")
    form_excluded_columns = ["airports"]
    column_searchable_list = ["name", "code"]

    def create_model(self, form):
        if flight_dao.get_country_by_code(form.code.data):
            form.code.errors.append("Country code already exists!")
            return False
        return super().create_model(form)

    def update_model(self, form, model):
        updated_country = flight_dao.get_country_by_code(form.code.data)
        if updated_country and updated_country.id != model.id:
            form.code.errors.append("Country code already exists!")
            return False
        return super().update_model(form, model)


class UserView(ModelView, AdminView):
    column_list = (
        "id",
        "first_name",
        "last_name",
        "email",
        "citizen_id",
        "phone",
        "role",
    )
    column_searchable_list = ["first_name", "last_name", "email", "citizen_id", "phone"]


class RouteAdmin(ModelView, AdminView):
    column_list = [
        "id",
        "depart_airport.name",
        "depart_airport.id",
        "arrive_airport.name",
        "arrive_airport.id",
    ]
    form_excluded_columns = ["flights"]
    column_searchable_list = ["depart_airport.name"]

    def create_model(self, form):

        route = flight_dao.get_route_by_airports(
            form.depart_airport.data.id, form.arrive_airport.data.id
        )
        if route:
            flash(f"Route already exists! {route}", "danger")
            return False
        return super().create_model(form)

    def update_model(self, form, model):
        existed_route = flight_dao.get_route_by_airports(
            form.depart_airport.data.id, form.arrive_airport.data.id
        )
        if existed_route and existed_route.id != model.id:
            flash(f"Route already exists! {existed_route}", "danger")
            return False
        return super().update_model(form, model)


class FlightAdmin(ModelView, AdminView):
    column_list = (
        "id",
        "route.depart_airport.name",
        "route.arrive_airport.name",
        "depart_time",
        "arrive_time",
        "aircraft.id",
        "aircraft.name",
        "aircraft.airline_name",
    )
    # column_searchable_list = ["route.depart_airport.name"]

    # column_labels = {
    #     "route.depart_airport.name": "Depart Airport",
    #     "route.arrive_airport.name": "Arrive Airport",
    #     "depart_time": "Departure Time",
    #     "arrive_time": "Arrival Time",
    #     "aircraft.id": "Aircraft ID",
    #     "aircraft.name": "Aircraft Name",
    #     "aircraft.airline_name": "Airline",
    # }

    form_excluded_columns = ["flight_seats"]

    def create_model(self, form):
        # Check depart_time < arrive_time
        if form.depart_time.data >= form.arrive_time.data:
            form.depart_time.errors.append("Depart time must be before arrive time!")
            form.arrive_time.errors.append("Depart time must be before arrive time!")
            return False
        # Check if aircraft is not available
        if not form.aircraft.data.is_available(
            form.depart_time.data, form.arrive_time.data
        ):
            form.aircraft.errors.append("Aircraft is not available at this time!")
            return False
        # Create seats for flight
        return super().create_model(form)

    def update_model(self, form, model):
        updated_airport = flight_dao.get_airport_by_code(form.code.data)
        if updated_airport and updated_airport.id != model.id:
            form.code.errors.append("Country code already exists!")
            return False
        return super().update_model(form, model)


class AirportAdmin(ModelView, AdminView):
    column_list = ("id", "name", "code", "country.name", "country.id")
    form_excluded_columns = ["intermediate_airports"]
    column_searchable_list = ["code", "name", "country.name"]

    def create_model(self, form):
        if flight_dao.get_airport_by_code(form.code.data):
            form.code.errors.append("Airport code already exists!")
            return False
        return super().create_model(form)

    def update_model(self, form, model):
        updated_airport = flight_dao.get_airport_by_code(form.code.data)
        if updated_airport and updated_airport.id != model.id:
            form.code.errors.append("Country code already exists!")
            return False
        return super().update_model(form, model)


class AircraftAdmin(ModelView, AdminView):
    # Hiển thị thêm airline_name
    column_list = ("id", "name", "airline_name")
    form_excluded_columns = ["seats", "flights"]
    form_extra_fields = {
        "aircraft_1seats": IntegerField(
            "Seats for 1st class", validators=[DataRequired(), NumberRange(min=1)]
        ),
        "aircraft_2seats": IntegerField(
            "Seats for 2nd class", validators=[DataRequired(), NumberRange(min=1)]
        ),
    }


class AirlineAdmin(ModelView, AdminView):
    column_list = ("id", "name")

    column_labels = {"id": "ID", "name": "Tên Hãng"}


class SeatClassAdmin(ModelView, AdminView):
    form_excluded_columns = ["seats"]


class RegulationView(ModelView, AdminView):
    form_excluded_columns = ["key"]
    can_create = False
    can_delete = False


class LogoutView(AuthenticatedView):
    @expose("/")
    def index(self):
        return logout_process()


class HomeView(AuthenticatedView):
    @expose("/")
    def index(self):
        return redirect("/")


admin = Admin(
    app,
    template_mode="bootstrap4",
    index_view=MyAdminView(name="Index"),
)

admin.add_view(HomeView(name="Home"))
admin.add_view(UserView(User, db.session, name="Users"))
admin.add_view(RouteAdmin(Route, db.session, name="Routes"))
admin.add_view(FlightAdmin(Flight, db.session, name="Flights"))
admin.add_view(AirportAdmin(Airport, db.session, name="Airports"))
admin.add_view(CountryAdmin(Country, db.session, name="Countries"))
admin.add_view(AircraftAdmin(Aircraft, db.session, name="Aircrafts"))
admin.add_view(AirlineAdmin(Airline, db.session, name="Airlines"))
admin.add_view(SeatClassAdmin(SeatClass, db.session, name="Seat Classes"))
admin.add_view(RegulationView(Regulation, db.session, name="Regulations"))
admin.add_view(LogoutView(name="Log out"))
