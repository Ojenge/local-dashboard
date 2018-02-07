# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import logging

import eventlet

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_socketio import SocketIO


DB_ROOT = os.path.dirname(os.path.abspath(__file__))

PROD_DATABASE = 'sqlite:////opt/apps/local-dashboard/prod.sqlite3'
DEFAULT_DATABASE = 'sqlite:///%s/dashboard.sqlite3' %(DB_ROOT)
DATABASES = {
    'development': DEFAULT_DATABASE,
    'production':  PROD_DATABASE
}
ENV = os.getenv('FLASK_CONFIG', 'development')
DATABASE_URI = DATABASES.get(ENV, DEFAULT_DATABASE)

app = Flask(__name__)

# Logging configuration
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
app.logger.addHandler(stream_handler)
# CORS
CORS(app)
# database settings
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
print('using database @ %s' % DATABASE_URI)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# we import this here so it is picked by alembic
from local_api.apiv1 import models
from local_api.apiv1 import utils
# login manager setup
from local_api.apiv1 import auth
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.request_loader(auth.load_user)
login_manager.unauthorized_handler(auth.unauthorized)
# register blueprints
from local_api.apiv1.controllers import api_blueprint
app.register_blueprint(api_blueprint, url_prefix='/api/v1')


socketio = SocketIO(app)

def send_system_state():
    socketio.emit('system', utils.get_system_state(), namespace='/dashboard')
    eventlet.call_after_global(5, send_system_state)

@socketio.on('connect', namespace='/dashboard')
def on_connect():
    app.logger.debug('user connected')
    socketio.emit('message', {'data': 1234}, namespace='/dashboard')

def create_app():
    eventlet.call_after_global(5, send_system_state)
    return app    
