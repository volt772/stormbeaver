from database.database_connection import fetch_multi, fetch_one, execute
from fastapi import HTTPException
from typing import Optional

from datetime import datetime

import json


def exists_current_weather():
    pass


def select_current_weather(
    stadium_code: str, league: str, updated_at: datetime
) -> Optional[dict]:
    """
    stadium_code : SOJ
        updated_at : 2025-07-22 09:00:00 (정시)
    """
    query = """
        SELECT count(*)
        FROM weather_download_log
        WHERE stadium_code = %s AND league = %s AND updated_at = %s
    """
    result = fetch_one(query, (stadium_code, league, updated_at))

    return result["count"] > 0


def insert_download_log(league: str, stadium_code: str, updated_at: datetime):
    insert_query = """
        INSERT INTO weather_download_log (league, stadium_code, updated_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (stadium_code, league)
        DO UPDATE SET updated_at = EXCLUDED.updated_at;
    """
    execute(
        query=insert_query,
        params=(league, stadium_code, updated_at),
    )


def insert_current_weather(stadium_code: str, weather_json: dict, updated_at):
    insert_query = """
        INSERT INTO current_weather (stadium_code, weather_json, updated_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (stadium_code, updated_at)
        DO NOTHING;
    """
    execute(
        query=insert_query,
        params=(stadium_code, json.dumps(weather_json), updated_at),
    )


def insert_forecast_weather(
    stadium_code: str, weather_json: dict, updated_at: datetime
):
    insert_query = """
        INSERT INTO forecast_weather (stadium_code, weather_json, updated_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (stadium_code, updated_at)
        DO NOTHING;
    """
    execute(
        query=insert_query, params=(stadium_code, json.dumps(weather_json), updated_at)
    )


def get_weather_response(stadium_code: str):
    current_row = get_latest_current_weather(stadium_code)
    forecast_row = get_latest_forecast_weather(stadium_code)

    if not current_row or not forecast_row:
        return None

    current = current_row["weather_json"]
    forecast = forecast_row["weather_json"]

    return {
        "current": {
            "weather": current["weather"],
            "main": current["main"],
            "name": current.get("name", ""),
            "cod": current.get("cod", 200),
        },
        "forecast": {
            "list": forecast["list"],
            "cnt": len(forecast["list"]),
            "cod": int(forecast.get("cod", 200)),
        },
    }


def get_latest_current_weather(stadium_code: str):
    query = """
        SELECT weather_json
        FROM current_weather
        WHERE stadium_code = %s
        ORDER BY updated_at DESC
        LIMIT 1
    """
    return fetch_one(query, (stadium_code,))


def get_latest_forecast_weather(stadium_code: str):
    query = """
        SELECT weather_json
        FROM forecast_weather
        WHERE stadium_code = %s
        ORDER BY updated_at DESC
        LIMIT 1
    """
    return fetch_one(query, (stadium_code,))
