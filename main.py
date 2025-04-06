import os
from datetime import datetime, timedelta, timezone

from loguru import logger
import functions_framework
from google.cloud import bigquery
import requests


client = bigquery.Client()


@functions_framework.http
def heaven_data_request_processor(request):
    request_args = request.args
    date_yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')

    date_from = datetime.strptime(request_args.get('date_from', date_yesterday), '%Y-%m-%d')
    date_to = datetime.strptime(request_args.get('date_to', date_yesterday), '%Y-%m-%d')

    try:
        # data_processing_result = orders_data_processing(date_from=date_from, date_to=date_to)
        # logger.success(data_processing_result)
        print(300)

        return 'heaven_data_request_processor', 200

    except Exception as exception:  # pylint: disable=broad-except
        logger.error(exception)

        return {"error": "Heaven's data request processing: Internal server error"}, 500
