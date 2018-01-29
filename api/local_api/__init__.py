# -*- coding: utf-8 -*-

from flask import Flask
from local_api.apiv1.controllers import api_blueprint

from local_api.apiv1 import auth
from flask_login import LoginManager

app = Flask(__name__)

manager = LoginManager()
manager.init_app(app)
manager.request_loader(auth.load_user)
manager.unauthorized_handler(auth.unauthorized)

app.register_blueprint(api_blueprint, url_prefix='/api/v1')
