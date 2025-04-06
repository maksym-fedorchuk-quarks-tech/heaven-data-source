import os
from datetime import datetime, timedelta, timezone
from loguru import logger
import functions_framework
from google.cloud import bigquery

client = bigquery.Client()


@functions_framework.http
def heaven_data_request_processor(request):
    date_yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
    date_from = datetime.strptime(request.args.get('date_from', date_yesterday), '%Y-%m-%d')
    date_to = datetime.strptime(request.args.get('date_to', date_yesterday), '%Y-%m-%d')

    try:
        print(300)
        return 'heaven_data_request_processor', 200

    except Exception as exception:
        logger.error(exception)
        return {"error": "Heaven's data request processing: Internal server error"}, 500
