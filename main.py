import os
import time
import hashlib
from random import randint

from datetime import datetime, timedelta, timezone
from loguru import logger
import functions_framework
from google.cloud import bigquery

from data_generator import generate_visitors_data, generate_registration_funnel_data, generate_prayers_data, generate_events_data

client = bigquery.Client()
endpoints_registry = {
    '/visits': generate_visitors_data,
    '/registration_funnel': generate_registration_funnel_data,
    '/prayers': generate_prayers_data,
    '/events': generate_events_data,
}

def generate_heavens_data(path:str, token:str, date_from:datetime, date_to:datetime):
    """
    Generates data for the specified Heaven service endpoint.
    
        
    Returns:
        dict: Generated data for the specified endpoint
    """
    generator_func = endpoints_registry[path]
    return generator_func(token, date_from, date_to)


def is_token_valid(token:str) -> bool:
    """
    Validates if the provided token exists and is still valid in the Heaven service.
    Returns True if token exists and is valid, False otherwise
    """
    query = (
        "SELECT COUNT(*) FROM `heavens_data.tokens` "
        "WHERE token = @token and valid_to >= CURRENT_TIMESTAMP()"
    )
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("token", "STRING", token)
        ]
    )
    results = client.query(query, job_config=job_config).result()
    return next(results).count > 0

def is_date_format_valid(date:str) -> bool:
    """
    Validates if the provided date string is in the correct format.
    Returns True if date format is valid, False otherwise
    """
    try:
        datetime.strptime(date, '%Y-%m-%d')
        return True
    except ValueError:
        return False

@functions_framework.http
def heaven_data_request_processor(request):
    """
    Main HTTP endpoint processor for the Heaven service API.
    Handles requests for various Heaven service data including visits, prayers, and events.
    
    Args:
        request: HTTP request object containing:
            - headers: Must include valid Authorization token
            - args: Optional date_from and date_to parameters (YYYY-MM-DD format)
            - path: API endpoint path
            
    Returns:
        dict: JSON response containing:
            - success (bool): Whether the request was successful
            - data (dict, optional): The requested data if successful
            - error (str, optional): Error message if request failed
            - status (int): HTTP status code
    """
    # Set response headers for JSON
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Authorization, Content-Type',
        'Available-Endpoints': ', '.join(endpoints_registry.keys())
    }

    token = request.headers.get('Authorization')
    if not token:
        return {
            "success": False,
            "error": "Authorization token is required",
            "status": 401
        }, 401, headers

    if len(token) != 64 or not is_token_valid(token):
        return {
            "success": False,
            "error": "Invalid token",
            "status": 403
        }, 403, headers

    date_yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
    date_from = request.args.get('date_from', date_yesterday)
    date_to = request.args.get('date_to', date_yesterday)

    # Validate dates format
    if not is_date_format_valid(date_from) or not is_date_format_valid(date_to):
        return {
            "success": False,
            "error": "Invalid date format. Use YYYY-MM-DD",
            "status": 400
        }, 400, headers

    # Convert strings to datetime objects for comparison
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')

    # Check if date_to is less than date_from
    if date_to_obj < date_from_obj:
        return {
            "success": False,
            "error": "date_to cannot be less than date_from",
            "status": 400
        }, 400, headers

    path = request.path
    if path not in endpoints_registry:
        return {
            "success": False,
            "error": "Invalid endpoint",
            "status": 404
        }, 404, headers

    try:
        time.sleep(1)
        data = generate_heavens_data(path, token, date_from_obj, date_to_obj)
        return {
            "success": True,
            "data": data,
            "status": 200
        }, 200, headers

    except Exception as exception:
        logger.error(exception)
        return {
            "success": False,
            "error": "Heaven's data request processing: Internal server error",
            "status": 500
        }, 500, headers
