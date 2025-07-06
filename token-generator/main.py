import hashlib
from datetime import datetime, timedelta, timezone

from loguru import logger
import functions_framework

from google.cloud import bigquery

TOKEN_TABLE_PATH = "publicdatasource.heavens_data.tokens"
POST_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json"
}


def generate_token_row(email: str) -> dict[str, str]:
    return {
        "email": email,
        "token": hashlib.shake_128(email.encode()).hexdigest(16),
        "valid_from": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "valid_to": (datetime.now(timezone.utc) + timedelta(days=365)).strftime("%Y-%m-%d")
    }


@functions_framework.http
def heaven_data_token(request):
    """Processes OPTIONS and POST requests to generate a token based on the provided email."""
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Email",
            "Access-Control-Max-Ag": "3600"
        }
        return '', 200, headers

    if request.method != 'POST':
        return {"error": "Method not allowed"}, 405, POST_HEADERS

    user_email = request.headers.get("Email")

    if not user_email:
        return {"error": "'Email' header is required"}, 400, POST_HEADERS

    client = bigquery.Client()
    new_token_row = generate_token_row(user_email)

    try:
        client.insert_rows_json(table=TOKEN_TABLE_PATH, json_rows=[new_token_row])
        logger.success(f"Rows successfully inserted for {user_email}")

        return {"status": 200, "token": new_token_row["token"]}, 200, POST_HEADERS

    except Exception as insert_exception:
        logger.error(f"Error while inserting new token for {user_email}: {insert_exception}")

        return {"status": 500, "error": "Internal Server Error"}, 500, POST_HEADERS
