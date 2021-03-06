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
requests = eventlet.import_patched('requests')

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
stream_handler.setLevel(logging.INFO)
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


NS_SIM_CONNECTIVITY = '/sim-connectivity'

socketio = SocketIO(app)

connected_clients = 0


def update_client_count(direction):
    """Update connected websocket client count

    We only send data downstream if there are connected clients.
    """
    global connected_clients
    connected_clients += direction
    app.logger.info('updated connected clients to: %d', connected_clients)


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
    app.logger.info('user connected / dashboard')
    socketio.emit('message', {'data': 'READY'}, namespace='/dashboard')


@socketio.on('connect', namespace='/diagnostics')
@auth.authenticated_only
def on_diagnostic_connect():
    update_client_count(1)
    eventlet.call_after_global(5, send_diagnostics_state)
    app.logger.info('user connected / diagnostics')
    socketio.emit('message', {'data': 'READY'}, namespace='/diagnostics')



@socketio.on('connect', namespace=NS_SIM_CONNECTIVITY)
@auth.authenticated_only
def on_sim_connectivity_connect():
    update_client_count(1)
    app.logger.info('user connected / sim-connectivity')
    socketio.emit('message', {'data': 'READY'}, namespace=NS_SIM_CONNECTIVITY)


@socketio.on('disconnect')
def on_disconnect():
    update_client_count(-1)
    app.logger.info('websocket client disconnected')


def get_retail_registration_token():
    device_mode = utils.get_device_mode()
    if not device_mode == "RETAIL":
        return
    while not utils.retail_device_registered():
        config = utils.get_retail_registration_config()
        url = config['url']
        headers = config['headers']
        post_data = {'login': config['login'] }
        try:
            request = requests.post(url, json=post_data, headers=headers)
            if request.status_code == 201:
                token_data = request.json()
                token = token_data['token']
                registered = token_data['registered']
                if registered:
                    utils.set_retail_device_registered()
                else:
                    utils.set_retail_registration_token(token)
        except requests.exceptions.ConnectionError:
            pass
        socketio.sleep(300)
    return


def create_app():
    socketio.start_background_task(get_retail_registration_token)
    return app
