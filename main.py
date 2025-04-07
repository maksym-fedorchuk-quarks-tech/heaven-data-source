import os
import time
import hashlib
from random import randint

from datetime import datetime, timedelta, timezone
from loguru import logger
import functions_framework
from google.cloud import bigquery

client = bigquery.Client()


def generate_installs_data(token):
    visitor_data = []
    for i in range(randint(701, 899)):
        install_id = hashlib.md5(f"{token}_{i}".encode()).hexdigest()
        visitor_data.append({
            "install_id": install_id,
            "install_time": datetime.now(timezone.utc).isoformat(),

            "utm_source": "test_source",
            "utm_campaign": "test_campaign",
            "initial_utm_medium": "test_medium",
            "referrer": "test_referrer",

        })

    return visitor_data

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

    if len(token) != 64 or not token_exists(token):
        return {"error": "Invalid token"}, 403

    date_yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
    date_from = datetime.strptime(request.args.get('date_from', date_yesterday), '%Y-%m-%d')
    date_to = datetime.strptime(request.args.get('date_to', date_yesterday), '%Y-%m-%d')

    try:
        time.sleep(1)
        visitor_data = generate_installs_data(token)
        return 'heaven_data_request_processor', 200

    except Exception as exception:
        logger.error(exception)
        return {"error": "Heaven's data request processing: Internal server error"}, 500
