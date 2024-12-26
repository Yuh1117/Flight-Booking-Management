from flask import flash
from flask_mail import Mail, Message
from flask import render_template
from app import mail


def validate_flight_seat_class(flight, seat_class):
    """
    1. Check if flight and seat class are valid
    2. Check if this flight is bookable now
    3. Check if flight has the seat class
    4. Check if there are available seats for the seat class
    """
    if not flight or not seat_class:
        flash("Invalid flight or seat class", "danger")
        return False
    if not flight.is_bookable_now():
        flash("You are not allowed to book this flight", "danger")
        return False
    remaining_seatclasses_and_info = flight.get_remaining_seatclasses_and_info()
    if seat_class.id not in remaining_seatclasses_and_info:
        flash("Flight doesn't have this seat class", "danger")
        return False
    if remaining_seatclasses_and_info[seat_class.id]["remaining"] == 0:
        flash("No available seats", "danger")
        return False
    return True


def send_booking_confirmation(reservation, email):
    msg_title = "Your Flight Ticket Confirmation"
    sender = "duongxummo@gmail.com"
    msg = Message(msg_title, sender=sender, recipients=[email])
    msg_body = "Here is your ticket:"
    data = {
        "app_name": "TICKET",
        "title": msg_title,
        "body": msg_body,
        "reservation": reservation,
    }
    msg.html = render_template("bookings/ticket_detail.html", data=data)
    try:
        mail.send(msg)
        return "Email sent with the ticket!"
    except Exception as e:
        print(e)
        return f"The email was not sent: {e}"
