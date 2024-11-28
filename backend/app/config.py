import os
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "6789lacachbonanhsong")
    DEBUG = True
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_HOST_PORT = os.getenv("MYSQL_HOST_PORT", "3306")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "flight_booking_system")
    MYSQL_ROOT_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD", "admin")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLITE_URI")
    # SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:{quote(MYSQL_ROOT_PASSWORD)}@{MYSQL_HOST}:{MYSQL_HOST_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
    CLOUDINARY_SECURE = os.getenv("CLOUDINARY_SECURE")
    CLOUDINARY_DEFAULT_AVATARS_PATH = os.getenv("CLOUDINARY_DEFAULT_AVATARS_PATH")
