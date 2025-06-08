import hashlib
from datetime import datetime, timedelta, timezone

from loguru import logger
import functions_framework

from google.cloud import bigquery

TOKEN_TABLE_PATH = "publicdatasource.heavens_data.tokens"


def generate_token_row(email: str) -> dict[str, str]:
    return {
        "email": email,
        "token": hashlib.shake_128(email.encode()).hexdigest(16),
        "valid_from": datetime.now(timezone.utc),
        "valid_to": datetime.now(timezone.utc) + timedelta(days=365)
    }


@functions_framework.http
def heaven_data_token(request):
    user_email = request.headers.get('Email')

    client = bigquery.Client()
    new_token_row = generate_token_row(user_email)

    insert_errors = client.insert_rows_json(table=TOKEN_TABLE_PATH, json_rows=[new_token_row])
    if insert_errors:
        logger.error(f"Errors while inserting new token: {insert_errors}")
        return {
            "status": 500,
            "error": "Internal Server Error"
        }

    else:
        logger.success(f"Rows successfully inserted for {user_email}")
        return {
            "status": 200,
            "token": new_token_row["token"]
        }
