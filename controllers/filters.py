from fastapi import APIRouter, Path
from pydantic import BaseModel
from database.validators import validate_user_id
from models.filters import (
    db_get_filters,
    db_add_filter,
    db_update_filter,
    db_delete_filter,
)


router = APIRouter(prefix="/api/filters", tags=["Filters"])


class FilterRequest(BaseModel):
    user_id: int
    name: str
    value: str


@router.get("/{user_id}")
def handle_get_filters(user_id: int = Path(..., description="사용자 ID")):
    """
    특정 사용자의 필터 목록을 조회하고, status 테이블의 모든 데이터를 반환합니다.
    """

    # 사용자 검증
    validate_user_id(user_id)

    return db_get_filters(user_id)


@router.post("")
def handle_add_filter(filter: FilterRequest):
    """새 필터 추가 후 ID 반환"""

    # 1️⃣ `user_id` 검증
    validate_user_id(filter.user_id)

    # 2️⃣ `db_add_filter()` 호출
    new_filter_id = db_add_filter(filter.user_id, filter.name, filter.value)

    return {"id": new_filter_id}


@router.put("/{filter_id}")
def handle_update_filter(
    filter_id: int = Path(..., description="업데이트할 필터 ID"),
    filter: FilterRequest = None,
):
    """기존 필터 정보 업데이트"""

    # 1️⃣ `user_id` 검증
    validate_user_id(filter.user_id)

    # 2️⃣ `db_update_filter()` 호출
    updated_filter_id = db_update_filter(
        filter_id, filter.user_id, filter.name, filter.value
    )

    return {"id": updated_filter_id}


@router.delete("/{filter_id}/{user_id}")
def handle_delete_filter(
    filter_id: int = Path(..., description="삭제할 필터 ID"),
    user_id: int = Path(..., description="사용자 ID"),
):
    """기존 필터 삭제"""

    # 1️⃣ `user_id` 검증
    validate_user_id(user_id)

    # 2️⃣ `db_delete_filter()` 호출
    deleted_filter_id = db_delete_filter(filter_id, user_id)

    return {"id": deleted_filter_id}
