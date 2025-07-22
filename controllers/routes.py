from fastapi import APIRouter, Path
from pydantic import BaseModel
from typing import List, Dict
from database.validators import validate_user_id
from models.routes import db_get_routes, db_add_route, db_update_route, db_delete_route


router = APIRouter(prefix="/api/routes", tags=["Routes"])


class RouteRequest(BaseModel):
    user_id: int
    name: str
    color: str


@router.get("/{user_id}")
def handle_get_routes(user_id: int = Path(..., description="조회할 사용자 ID")) -> List[Dict]:
    """사용자의 routes + 기본 admin(1) routes 조회"""

    validate_user_id(user_id)
    return db_get_routes(user_id)


@router.post("")
def handle_add_route(route: RouteRequest):
    """새로운 route 추가 후 ID 반환"""

    # 1️⃣ `user_id` 검증
    validate_user_id(route.user_id)

    # 2️⃣ `db_add_route()` 호출
    new_route_id = db_add_route(route.user_id, route.name, route.color)

    return {"id": new_route_id}


@router.put("/{route_id}")
def handle_update_route(route_id: int, route: RouteRequest):
    """기존 route 정보 업데이트"""

    # 1️⃣ `user_id` 검증
    validate_user_id(route.user_id)

    # 2️⃣ `db_update_route()` 호출
    updated_route_id = db_update_route(route_id, route.user_id, route.name, route.color)

    return {"id": updated_route_id}


@router.delete("/{route_id}/{user_id}")
def handle_delete_route(
    route_id: int = Path(..., description="삭제할 경로 ID"),
    user_id: int = Path(..., description="사용자 ID"),
):
    """기존 route 삭제"""

    # 1️⃣ `user_id` 검증
    validate_user_id(user_id)

    # 2️⃣ `db_delete_route()` 호출
    deleted_route_id = db_delete_route(route_id, user_id)

    return {"id": deleted_route_id}
