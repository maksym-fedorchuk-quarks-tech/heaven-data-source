import hashlib
from datetime import datetime, timezone
from random import randint


def generate_visitors_data(token, date_from, date_to):
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

def generate_registration_funnel_data(token, date):
    return {}

def generate_prayers_data(token, date):
    return {}

def generate_events_data(token, date):
    return {}