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
    'data': [],
    'dataframe': None
}

# Teachers cache - stores all teachers data
_teachers_cache = {
    'data': None,
    'dataframe': None
}

# Subjects cache - stores all calendar subjects data
_subjects_cache = {
    'data': None,
    'dataframe': None
}

@data_blueprint.route('/programs', methods=['GET'])
def get_programs():
    """Get programs, optionally filtered by type."""
    type_filter = request.args.get('type')
    format_type = request.args.get('format', 'json')  # json or csv
    
    if not _programs_cache['data']:
        refresh_programs_dict()
    
    filtered = filter(lambda p: type_filter is None or p.get("type") == type_filter, _programs_cache['data'])
    filtered_list = list(filtered)
    
    if format_type == 'csv' and _programs_cache['dataframe'] is not None:
        # Return as CSV
        import pandas as pd
        df = _programs_cache['dataframe']
        if type_filter:
            df = df[df['Type'] == type_filter]
        csv_data = df.to_csv(index=False)
        return csv_data, 200, {'Content-Type': 'text/csv', 
                               'Content-Disposition': 'attachment; filename=programs.csv'}
    
    result = {
        'programs': filtered_list,
        'count': len(filtered_list)
    }
    return jsonify(result)


@data_blueprint.route('/programs/refresh', methods=['POST'])
@auth.login_required
def refresh_programs():
    """Refresh the programs cache."""
    try:
        refresh_programs_dict()
        return jsonify({
            "result": True,
            "message": f"Cache refreshed successfully",
            "programs_count": len(_programs_cache['data']),
        }), 200
        
    except Exception as e:
        logging.getLogger('root').error(f"Failed to refresh cache: {e}")
        return jsonify({
            "result": False,
            "message": f"Failed to refresh cache: {str(e)}"
        }), 500

def refresh_programs_dict():
    """Refresh programs cache from Airtable."""
    request_obj = iway_requests.GetAvailableProgramsRequest()
    
    # Get as list for JSON responses
    list_of_programs = request_obj.apply()
    _programs_cache['data'] = [program.to_dict() for program in list_of_programs]
    
    # Also store as DataFrame for CSV exports and analytics
    try:
        _programs_cache['dataframe'] = request_obj.apply_as_dataframe()
    except Exception as e:
        logging.getLogger('root').warning(f"Could not cache DataFrame: {e}")
        _programs_cache['dataframe'] = None
    
    logging.getLogger('root').info(f"Cache initialized with {len(list_of_programs)} programs")


def refresh_teachers_dict():
    """Refresh teachers cache from Airtable."""
    request_obj = iway_requests.GetTeachersRequest()
    
    # Get as DataFrame
    teachers_df = request_obj.apply()
    _teachers_cache['dataframe'] = teachers_df
    
    # Also store as list of dicts for JSON responses
    _teachers_cache['data'] = teachers_df.to_dict('records') if not teachers_df.empty else []
    
    logging.getLogger('root').info(f"Cache initialized with {len(teachers_df)} teachers")


def refresh_subjects_dict():
    """Refresh subjects cache from Airtable."""
    request_obj = iway_requests.CalendarDataRequest()
    
    # Get as DataFrame
    subjects_df = request_obj.apply()
    _subjects_cache['dataframe'] = subjects_df
    
    # Also store as list of dicts for JSON responses
    _subjects_cache['data'] = subjects_df.to_dict('records') if not subjects_df.empty else []
    
    logging.getLogger('root').info(f"Cache initialized with {len(subjects_df)} subjects")


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


@data_blueprint.route('/events', methods=['POST'])
def calendar_data():
    """Get calendar event data joined with subjects."""
    data = request.form or request.get_json()
    format_type = request.args.get('format', 'json')  # json or csv
    
    try:
        # Use the new joined request that combines events and subjects
        # In list_mode, we don't use caches, so no need to initialize them
        joined_request = iway_requests.CalendarEventsWithSubjectsRequest(
            data, 
            cached_teachers_df=None,
            cached_subjects_df=None,
            list_mode=True  # Fetch only minimal fields for performance
        )
        merged_df = joined_request.apply()
        
        if format_type == 'csv':
            # Return combined data as CSV (all fields for CSV)
            csv_data = merged_df.to_csv(index=False)
            return csv_data, 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': 'attachment; filename=calendar_events.csv'
            }
        
        # Return as JSON with limited fields
        events_list = joined_request.apply_as_list()
        
        result = {
            'events': events_list,
            'count': len(events_list)
        }
        
        return jsonify({
            "result": True,
            "data": result
        })
    except Exception as e:
        logging.getLogger('root').error(f"Error fetching calendar data: {e}")
        return jsonify({
            "result": False,
            "message": f"Invalid data: {str(e)}"
        }), 400

@data_blueprint.route('/events/<event_id>', methods=['GET'])
def get_event_by_id(event_id):
    """Get a specific calendar event by ID with subject and teacher information."""
    try:
        # Get event type from query params (default to "masa")
        event_type = request.args.get('type', 'masa')
        
        # Ensure caches are initialized
        if _teachers_cache['dataframe'] is None:
            refresh_teachers_dict()
        if _subjects_cache['dataframe'] is None:
            refresh_subjects_dict()
        
        # Use the optimized request that fetches only the specific event
        event_request = iway_requests.GetSpecificEventRequest(
            event_id=event_id,
            event_type=event_type,
            cached_teachers_df=_teachers_cache['dataframe'],
            cached_subjects_df=_subjects_cache['dataframe']
        )
        event_dict = event_request.apply_as_dict()
        
        if not event_dict:
            return jsonify({
                "result": False,
                "message": f"Event with ID {event_id} not found"
            }), 404
        
        return jsonify({
            "result": True,
            "data": event_dict
        })
    except Exception as e:
        logging.getLogger('root').error(f"Error fetching event by ID: {e}")
        return jsonify({
            "result": False,
            "message": f"Invalid request: {str(e)}"
        }), 400

