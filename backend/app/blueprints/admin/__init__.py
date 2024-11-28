from flask import Blueprint

# Create the main blueprint
admin_bp = Blueprint("admin", __name__)

# Import routes to register them with the blueprint
from . import routes
