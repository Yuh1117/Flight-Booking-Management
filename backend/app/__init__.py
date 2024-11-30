from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import cloudinary

from app.config import Config


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"

cloudinary.config(
    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET,
    secure=Config.CLOUDINARY_SECURE,
)

from app.blueprints.main import main_bp
from app.blueprints.auth import auth_bp
from app.blueprints.admin import admin_bp
from app.blueprints.errors import errors

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(errors)
