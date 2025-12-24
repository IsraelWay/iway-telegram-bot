#  Author: Ainur Iagudin. Copyright (c) 2025.
from flask import jsonify, Blueprint, request
from flask_httpauth import HTTPTokenAuth
from server import iway_requests
import logging
import re

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

data_blueprint = Blueprint('data', __name__)
auth = HTTPTokenAuth(scheme='Bearer', header='Authorization')

# In-memory cache - simple and persistent until manual refresh
_programs_cache = {
    'data': []
}

@data_blueprint.route('/programs', methods=['GET'])
def get_programs():
    type = request.args.get('type')
    if not _programs_cache['data']:
        refresh_programs()
    filtered = filter(lambda p: type is None or p["type"] == type, _programs_cache['data'])
    result = {
        'programs': list(filtered)
    }
    print(result)
    return jsonify(result)


@data_blueprint.route('/programs/refresh', methods=['POST'])
@auth.login_required
def refresh_programs():
    try:
        refresh_programs_dict()
        return jsonify({
            "result": True,
            "message": f"Cache refreshed successfully",
            "programs_count": len(_programs_cache['programs']),
        }), 200
        
    except Exception as e:
        logging.getLogger('root').error(f"Failed to refresh cache: {e}")
        return jsonify({
            "result": False,
            "message": f"Failed to refresh cache: {str(e)}"
        }), 500

def refresh_programs_dict():
    list_of_programs = iway_requests.GetAvailableProgramsRequest().apply()
    _programs_cache['data'] = [program.to_dict() for program in list_of_programs]
    logging.getLogger('root').info(f"Cache initialized with {len(list_of_programs)} programs")

@data_blueprint.route('/register', methods=['POST'])
def add_new_record():
    data = request.form or request.get_json()
    try:
        air_request = iway_requests.RegisterUserRequest(data)
        result = air_request.apply()
        if not result:
            return jsonify({
                "result": False,
                "message": "Failed to register user"
            }), 500
        return jsonify({
            "result": True,
            "message": "User registered successfully"
        }), 200
    except Exception as e:
        return jsonify({
            "result": False,
            "message": f"Invalid data: {str(e)}"
        }), 400
    