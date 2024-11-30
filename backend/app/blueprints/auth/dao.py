import cloudinary.api
import random as rd


from app import db, bcrypt
from app import Config
from .models import User, UserRole


def get_cloudinary_default_imgs():
    try:
        print("Fetching default images from cloudinary...")
        resources = cloudinary.api.resources_by_asset_folder(
            Config.CLOUDINARY_DEFAULT_AVATARS_PATH, fields=["secure_url"]
        )
        return [resource["secure_url"] for resource in resources["resources"]]
    except cloudinary.exceptions.Error as e:
        print(f"An error occurred: {e}")
        return []


DEFAULT_PROFILE_PICTURES = get_cloudinary_default_imgs()


def randomize_profile_img():
    return rd.choice(DEFAULT_PROFILE_PICTURES)


def get_user_by_id(user_id):
    return User.query.get(user_id)


def add_user(
    email,
    password,
    citizen_id,
    first_name,
    last_name,
    phone,
    role=UserRole.USER,
    avatar=None,
):
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(
        email=email, 
        password=hashed_password,
        role=role,
        citizen_id=citizen_id,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        avatar=avatar if avatar else randomize_profile_img(),
    )
    db.session.add(user)
    db.session.commit()


def authenticate_user(email, password):
    user = get_user_by_email(email)
    if user and bcrypt.check_password_hash(user.password, password):
        return user
    return None


def get_users(limit=1000):
    return User.query.limit(limit).all()


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def get_user_by_citizen_id(citizen_id):
    return User.query.filter_by(citizen_id=citizen_id).first()
