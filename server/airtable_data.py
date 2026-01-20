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
        joined_request = iway_requests.CalendarEventsWithSubjectsRequest(data)
        merged_df = joined_request.apply()
        
        if format_type == 'csv':
            # Return combined data as CSV
            csv_data = merged_df.to_csv(index=False)
            return csv_data, 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': 'attachment; filename=calendar_events.csv'
            }
        
        # Return as JSON
        result = {
            'events': merged_df.to_dict('records') if not merged_df.empty else [],
            'count': len(merged_df)
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


@data_blueprint.route('/programs/analytics', methods=['GET'])
def programs_analytics():
    """Get analytics on programs data."""
    if not _programs_cache['dataframe'] is not None:
        refresh_programs_dict()
    
    df = _programs_cache['dataframe']
    
    if df is None or df.empty:
        return jsonify({
            "result": False,
            "message": "No data available"
        }), 404
    
    try:
        analytics = {
            'total_programs': len(df),
            'by_type': df['Type'].value_counts().to_dict() if 'Type' in df.columns else {},
            'by_city': df['Город'].value_counts().to_dict() if 'Город' in df.columns else {},
            'unique_cities': int(df['Город'].nunique()) if 'Город' in df.columns else 0,
            'unique_types': int(df['Type'].nunique()) if 'Type' in df.columns else 0
        }
        
        return jsonify({
            "result": True,
            "analytics": analytics
        })
    except Exception as e:
        logging.getLogger('root').error(f"Error calculating analytics: {e}")
        return jsonify({
            "result": False,
            "message": f"Error calculating analytics: {str(e)}"
        }), 500
