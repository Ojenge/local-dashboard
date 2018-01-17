# -*- coding: utf-8 -*-

"""
API Controllers for the local dashboard
"""

from flask import Blueprint, jsonify

from utils import get_storage_status

api_blueprint = Blueprint('apiv1', __name__)

@api_blueprint.route('/system')
def system_api():
    """Returns a JSON struct of the system API
    :ret string
    """
    state = dict(
        storage = get_storage_status()
    )
    return jsonify(state)
