# -*- coding: utf-8 -*-
import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate




DB_ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATABASE = 'sqlite:///%s/dashboard.sqlite3' %(DB_ROOT)

app = Flask(__name__)



# database settings
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI',
                                                  DEFAULT_DATABASE) 
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# we import this here so it is picked by alembic
from local_api.apiv1 import models



# login manager setup
from local_api.apiv1 import auth

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.request_loader(auth.load_user)
login_manager.unauthorized_handler(auth.unauthorized)


# register blueprints
from local_api.apiv1.controllers import api_blueprint

app.register_blueprint(api_blueprint, url_prefix='/api/v1')
