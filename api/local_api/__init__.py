from flask import Flask
from local_api.apiv1.controllers import api_blueprint


app = Flask(__name__)


app.register_blueprint(api_blueprint, url_prefix='/api/v1')
