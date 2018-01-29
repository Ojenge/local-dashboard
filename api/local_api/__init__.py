# -*- coding: utf-8 -*-

from flask import Flask
from flask_login import LoginManager


from local_api.apiv1.controllers import api_blueprint
from local_api.apiv1 import auth

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.request_loader(auth.load_user)
login_manager.unauthorized_handler(auth.unauthorized)

app.register_blueprint(api_blueprint, url_prefix='/api/v1')
