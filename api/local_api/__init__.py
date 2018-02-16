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

connected_clients = 0


def update_client_count(direction):
    """Update connected websocket client count

    We only send data downstream if there are connected clients.
    """
    global connected_clients
    connected_clients += direction
    app.logger.debug('updated connected clients to: %d', connected_clients)


def send_system_state():
    """Sends system state payload to connected websocket clients.

    Also, queues up the next task to send system state.

    :return: None
    """
    global connected_clients
    if connected_clients > 0:
        socketio.emit('system', utils.get_system_state(), namespace='/dashboard')
        eventlet.call_after_global(5, send_system_state)
    else:
        app.logger.info('skipping sending system state | no clients conected')


def send_diagnostics_state():
    """Sends device diagnostics state payload to connected websocket clients.

    Also, queues up the next task to send diagnostic data.

    :return: None
    """
    global connected_clients
    if connected_clients > 0:
        socketio.emit('diagnostics', utils.get_diagnostics_data(), namespace='/diagnostics')
        eventlet.call_after_global(5, send_diagnostics_state)
    else:
        app.logger.info('skipping sending diagnostic data | no connected clients')


@socketio.on('connect', namespace='/dashboard')
@auth.authenticated_only
def on_dashboard_connect():
    update_client_count(1)
    eventlet.call_after_global(5, send_system_state)
    app.logger.debug('user connected / dashboard')
    socketio.emit('message', {'data': 'READY'}, namespace='/dashboard')


@socketio.on('connect', namespace='/diagnostics')
@auth.authenticated_only
def on_diagnostic_connect():
    update_client_count(1)
    eventlet.call_after_global(5, send_diagnostics_state)
    app.logger.debug('user connected / diagnostics')
    socketio.emit('message', {'data': 'READY'}, namespace='/diagnostics')


@socketio.on('disconnect')
def on_disconnect():
    update_client_count(-1)
    app.logger.debug('websocket client disconnected')


def create_app():
    return app    
