from fastapi import HTTPException
from database.database_connection import fetch_one


# ✅ 랜덤 이름 생성 함수 (이메일 + 랜덤 5글자)
def generate_random_name(email: str) -> str:
    email_id = email.split("@")[0]
    random_chars = "".join(random.choices(string.ascii_uppercase, k=5))
    return f"{email_id}{random_chars}"


def validate_user_id(user_id: int):
    """
    `user_id`가 유효한지 확인
    - 존재하지 않는 `user_id`일 경우 `400 Bad Request` 반환
    - `user_id=1`(admin)일 경우 `UPDATE` 및 `DELETE` 불가능
    """
    # ✅ `user_id` 존재 여부 확인
    user_check_query = "SELECT id FROM users WHERE id = %s"
    user_exists = fetch_one(user_check_query, (user_id,))

    if not user_exists:
        raise HTTPException(status_code=400, detail="User ID does not exist")

    # ✅ `user_id=1`인 경우 예외 처리
    if user_id == 1:
        raise HTTPException(
            status_code=400, detail="Admin routes cannot be modified or deleted"
        )


def validate_status_and_route(status_id: int, route_id: int):
    """status_id 및 route_id가 유효한지 검증"""

    # `status_id` 검증
    status_check_query = "SELECT id FROM status WHERE id = %s;"
    valid_status = fetch_one(status_check_query, (status_id,))
    if not valid_status:
        raise HTTPException(status_code=400, detail="Invalid status_id")

    # `route_id` 검증
    route_check_query = "SELECT id FROM route WHERE id = %s;"
    valid_route = fetch_one(route_check_query, (route_id,))
    if not valid_route:
        raise HTTPException(status_code=400, detail="Invalid route_id")
