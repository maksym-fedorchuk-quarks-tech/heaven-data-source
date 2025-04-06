import os
import time
from datetime import datetime, timedelta, timezone
from loguru import logger
import functions_framework
from google.cloud import bigquery

client = bigquery.Client()


def generate_visitor_data(token):
    return {
        "token": token,
        "visitors": [
            {"id": 1, "name": "Visitor A", "visit_time": datetime.now(timezone.utc).isoformat()},
            {"id": 2, "name": "Visitor B", "visit_time": datetime.now(timezone.utc).isoformat()},
        ]
    }


def token_exists(token):
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
    return any(row.count > 0 for row in results)


@functions_framework.http
def heaven_data_request_processor(request):
    token = request.headers.get('Authorization')
    if not token:
        return {"error": "Authorization token is required"}, 401

    if not token_exists(token):
        return {"error": "Invalid token"}, 403

    date_yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
    date_from = datetime.strptime(request.args.get('date_from', date_yesterday), '%Y-%m-%d')
    date_to = datetime.strptime(request.args.get('date_to', date_yesterday), '%Y-%m-%d')

    try:
        time.sleep(1)
        visitor_data = generate_visitor_data(token)
        return 'heaven_data_request_processor', 200

    except Exception as exception:
        logger.error(exception)
        return {"error": "Heaven's data request processing: Internal server error"}, 500
