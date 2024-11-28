from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app import app, db

admin = Admin(app, name="E-commerce Administration", template_mode='bootstrap4')
admin.init_app(app, template_folder='templates', base_template='dashborad.html')