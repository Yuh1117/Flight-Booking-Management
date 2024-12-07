import os
from urllib.parse import quote
from dotenv import load_dotenv
import json
from pathlib import Path

load_dotenv()


class FlaskConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "6789lacachbonanhsong")
    DEBUG = True
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_HOST_PORT = os.getenv("MYSQL_HOST_PORT", "3306")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "flight_booking_system")
    MYSQL_ROOT_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD", "123456")
    # SQLALCHEMY_DATABASE_URI = os.getenv("SQLITE_URI")
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:{quote(MYSQL_ROOT_PASSWORD)}@{MYSQL_HOST}:{MYSQL_HOST_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class CloudinaryConfig:
    CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    API_KEY = os.getenv("CLOUDINARY_API_KEY")
    API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
    SECURE = os.getenv("CLOUDINARY_SECURE")
    DEFAULT_AVATARS_PATH = os.getenv("CLOUDINARY_DEFAULT_AVATARS_PATH")


CLIENT_CONFIG_PATH = Path(__file__).parent.parent / "client_secret.json"


class GoogleAuthConfig:
    CLIENT_CONFIG = json.loads(CLIENT_CONFIG_PATH.read_text())
    SCOPES = [
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
    ]
    REDIRECT_URI = CLIENT_CONFIG["web"]["redirect_uris"][0]
