from fastapi import APIRouter, Path, Query
from pydantic import BaseModel
from typing import Optional, Union
from database.validators import validate_user_id
from models.settings import db_get_setting, db_get_all_settings, db_add_setting


router = APIRouter(prefix="/api/settings", tags=["Settings"])


class SettingsRequest(BaseModel):
    user_id: int
    key: str
    value: Union[str, int]  # value는 문자열 또는 정수 가능


@router.get("/{user_id}")
def handle_get_settings(
    user_id: int = Path(..., description="사용자 ID"),
    key: Optional[str] = Query(None, description="설정 키 값 (선택 사항)"),
):
    """사용자의 특정 설정 또는 모든 설정을 조회"""

    """사용자의 특정 설정 또는 모든 설정을 조회"""

    if key:
        return db_get_setting(user_id, key)
    else:
        return db_get_all_settings(user_id)


@router.post("")
def handle_add_setting(setting: SettingsRequest):
    """환경 설정 저장 (UPSERT 방식)"""

    # 1️⃣ `user_id` 검증
    validate_user_id(setting.user_id)

    # 2️⃣ `db_add_setting()` 호출
    return db_add_setting(setting.user_id, setting.key, setting.value)
