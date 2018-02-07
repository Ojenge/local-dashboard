# -*- coding: utf-8 -*-

from flask_socketio import SocketIO, emit
from local_api import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app)
