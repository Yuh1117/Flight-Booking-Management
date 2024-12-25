from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import DateTimeLocalField
from wtforms import SubmitField
from wtforms import BooleanField
from wtforms import TelField
from wtforms import HiddenField
from wtforms import SelectField
from wtforms import ValidationError
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Email
from wtforms.validators import EqualTo
from datetime import datetime as dt
from flask_login import current_user
from flask import flash
from . import dao


class FlightSchedulingForm(FlaskForm):
    flight_code = StringField("Flight Code", validators=[DataRequired()])
    departure_airport = SelectField(
        "Departure Airport",
        validators=[DataRequired()],
        render_kw={
            "class": "selectpicker",
            "data-live-search": "true",
            "title": "Select departure airport",
        },
    )
    arrival_airport = SelectField(
        "Arrival Airport",
        validators=[DataRequired()],
        render_kw={
            "class": "selectpicker",
            "data-live-search": "true",
            "title": "Select arrival airport",
        },
    )
    aircraft = SelectField(
        "Aircraft",
        validators=[DataRequired()],
        render_kw={
            "class": "selectpicker",
            "data-live-search": "true",
            "title": "Select aircraft",
        },
    )
    departure_time = DateTimeLocalField("Departure Time", validators=[DataRequired()])
    arrival_time = DateTimeLocalField("Arrival Time", validators=[DataRequired()])
    submit = SubmitField("Submit")

    def validate(self, extra_validators=None):
        if not super().validate():
            return False
        if self.departure_airport.data == self.arrival_airport.data:
            self.departure_airport.errors.append(
                "Departure airport must be different from arrival airport!"
            )
            self.arrival_airport.errors.append(
                "Arrival airport must be different from departure airport!"
            )
            return False
        #
        # Validate time
        #
        if self.departure_time.data < dt.now():
            self.departure_time.errors.append(
                "Departure time must be later than current time!"
            )
            return False
        if self.departure_time.data >= self.arrival_time.data:
            self.arrival_time.errors.append(
                "Arrival time must be later than departure time!"
            )
            return False
        flight_minutes = (
            self.arrival_time.data - self.departure_time.data
        ).total_seconds() // 60
        min_f_duration = dao.get_min_flight_duration()
        max_f_duration = dao.get_max_flight_duration()
        if not min_f_duration <= flight_minutes <= max_f_duration:
            self.arrival_time.errors.append(
                f"Flight duration must be between {min_f_duration} - {max_f_duration} minutes!"
            )
            return False
        #
        # Validate aircraft
        #
        aircraft = dao.get_aircraft_by_id(self.aircraft.data)
        if not aircraft:
            self.aircraft.errors.append("Aircraft not found!")
            return False
        if not aircraft.is_available(self.departure_time.data, self.arrival_time.data):
            self.aircraft.errors.append("Aircraft is not available!")
            return False
        return True
