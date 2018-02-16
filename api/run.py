# -*- coding: utf-8 -*-

from local_api import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app)
