from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def calcular_periodo(period):
    hoje = datetime.now(ZoneInfo("UTC"))
    period_mapping = {
        "today": (hoje, hoje),
        "yesterday": (hoje - timedelta(days=1), hoje - timedelta(days=1)),
        "last_7d": (hoje - timedelta(days=7), hoje),
        "last_14d": (hoje - timedelta(days=14), hoje),
        "last_30d": (hoje - timedelta(days=30), hoje),
        "this_month": (hoje.replace(day=1), hoje),
        "last_month": ((hoje.replace(day=1) - timedelta(days=1)).replace(day=1), hoje.replace(day=1) - timedelta(days=1)),
        "max": (datetime(2022, 2, 12, tzinfo=ZoneInfo("UTC")), hoje)
    }
    return period_mapping.get(period, (hoje - timedelta(days=7), hoje))
