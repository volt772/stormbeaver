from fastapi import APIRouter, Path
from pydantic import BaseModel
from typing import Optional
from models.users import db_add_user, db_get_user


router = APIRouter(prefix="/api/users", tags=["Users"])


# 사용자 등록 모델
class UserRegisterRequest(BaseModel):
    email: str
    profile: Optional[str]


@router.post("")
def handle_register_user(user: UserRegisterRequest):
    """이메일이 존재하면 profile 업데이트, 없으면 새 사용자 삽입 후 userId 반환"""
    return db_add_user(user.email, user.profile)


@router.get("/{user_id}")
def handle_get_user(user_id: int = Path(..., description="사용자 ID")):
    """사용자 정보 조회"""
    return db_get_user(user_id)
