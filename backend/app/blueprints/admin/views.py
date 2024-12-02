from flask import redirect, url_for, request
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from app.blueprints.auth.models import UserRole
import app
from flask_admin import expose


from app.blueprints.auth.models import User


class MyAdminViews(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.role == UserRole.ADMIN
        return False


app.admin.add_view(MyAdminViews(User, app.db.session))
