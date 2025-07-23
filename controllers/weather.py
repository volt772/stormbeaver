from fastapi import APIRouter, Path, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from api.weather_request import fetch_current_weather, fetch_forecast_weather
from utils.helpers import get_current_hour_timestamp
from models.weather import (
    select_current_weather,
    insert_download_log,
    insert_current_weather,
    insert_forecast_weather,
    get_weather_response,
)
from base.weather_schema import WeatherQuery

import asyncio


router = APIRouter(prefix="/api/weather", tags=["Weather"])


# 사용자 등록 모델
@router.get("/")
async def get_openapi_weather(query: WeatherQuery = Depends()):
    # 실제 데이터 처리는 model.weather에서 구현 예정

    # 카운트 검사
    current_date = get_current_hour_timestamp()
    isExist = select_current_weather(query.stadium_code, query.league, current_date)

    print("IS EXISTS : ", isExist)
    if not isExist:
        # 없으면 네트워크 요청 후, DB 쿼리
        await get_weather(query)

    result = get_weather_response(query.stadium_code)

    if not result:
        raise HTTPException(status_code=404, detail="날씨 데이터 없음")

    return result


async def get_weather(query: WeatherQuery):
    current, forecast = await asyncio.gather(
        fetch_current_weather(query),
        fetch_forecast_weather(query),
    )

    if not current or not forecast:
        raise HTTPException(status_code=502, detail="날씨 API 응답이 올바르지 않습니다.")

    # ✅ 날씨 다운로드 로그 기록
    insert_download_log(
        league=query.league,  # query에 league 포함돼 있어야 함
        stadium_code=query.stadium_code,
        updated_at=get_current_hour_timestamp(),  # 예: 정각 기준
    )
    # 기록넣고
    insert_current_weather(
        stadium_code=query.stadium_code,
        weather_json=current,  # API 응답 전체 dict
        updated_at=get_current_hour_timestamp(),
    )

    insert_forecast_weather(
        stadium_code=query.stadium_code,
        weather_json=forecast,  # API에서 받은 forecast 응답 전체
        updated_at=get_current_hour_timestamp(),
    )
