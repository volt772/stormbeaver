import os
import httpx
from dotenv import load_dotenv
from pathlib import Path
from base.weather_schema import WeatherQuery

env_mode = os.getenv("ENV", "development")
env_file = f"/home/volt772/work/source/stormbeaver/.env"

if Path(env_file).exists():
    load_dotenv(env_file)
else:
    raise FileNotFoundError(f".env file not found: {env_file}")

BASE_URL = os.getenv("BASE_URL", "https://api.example.com")  # 기본값도 설정 가능
API_KEY = os.getenv("API_KEY", "XXX1234")


async def fetch_current_weather(query: WeatherQuery):
    url = f"{BASE_URL}/data/2.5/weather"
    params = {
        "lat": query.lat,
        "lon": query.lon,
        "appid": API_KEY,
        "units": query.units,
        "lang": query.lang,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        return response.json()


async def fetch_forecast_weather(query: WeatherQuery):
    url = f"{BASE_URL}/data/2.5/forecast"
    params = {
        "lat": query.lat,
        "lon": query.lon,
        "appid": API_KEY,
        "units": query.units,
        "lang": query.lang,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        return response.json()
