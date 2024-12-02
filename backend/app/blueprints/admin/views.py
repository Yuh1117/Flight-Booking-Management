from flask import redirect, url_for, request
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from app.blueprints.auth.models import UserRole
from flask_admin import Admin, AdminIndexView, BaseView
from app import app, db


from app.blueprints.auth.models import User


class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class AdminView(AuthenticatedView):
    def is_accessible(self):
        return super().is_accessible() and current_user.role == UserRole.ADMIN


class MyAdminView(AdminIndexView, AdminView):
    pass


class UserView(ModelView, AdminView):
    pass


admin = Admin(app, name="Admin", template_mode="bootstrap4", index_view=MyAdminView())
admin.add_view(UserView(User, db.session, name="Users"))
