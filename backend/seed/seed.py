import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime as dt
import json
from sqlalchemy import inspect
from app import app, db
from app.blueprints.auth import dao as auth_dao
from app.blueprints.auth.models import UserRole


def seed_users():
    with open("backend/seed/data/users.json") as f:
        users = json.load(f)
        for user in users:
            user["role"] = UserRole(user["role"])
            auth_dao.add_user(**user)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_users()
        db.session.commit()
        print("Data seeded successfully.")
        print(inspect(db.engine).get_table_names())
