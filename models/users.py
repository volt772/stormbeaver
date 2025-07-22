from database.database_connection import fetch_one, execute
from fastapi import HTTPException
from utils.helpers import generate_random_name


def db_add_user(email: str, profile: str):
    """이메일이 존재하면 profile 업데이트, 없으면 새 사용자 삽입 후 userId 반환"""

    # 1️⃣ 기존 사용자 ID 조회
    select_query = "SELECT id FROM users WHERE email = %s"
    existing_user = fetch_one(select_query, (email,))

    if existing_user:
        # 2️⃣ 기존 사용자 정보 업데이트
        update_query = """
            UPDATE users SET profile = %s, created_at = EXTRACT(EPOCH FROM now()) * 1000
            WHERE email = %s
        """
        execute(query=update_query, params=(profile, email))
        return {"user_id": existing_user["id"]}  # 기존 사용자 ID 반환

    else:
        # 3️⃣ 새로운 사용자 삽입
        insert_query = """
            INSERT INTO users (name, email, profile, created_at)
            VALUES (%s, %s, %s, EXTRACT(EPOCH FROM now()) * 1000)
            RETURNING id
        """
        generated_name = generate_random_name(email)
        new_user_id = execute(
            query=insert_query,
            params=(generated_name, email, profile),
            returning=True,
        )

        if new_user_id:
            return {"user_id": new_user_id["id"]}
        else:
            raise HTTPException(status_code=500, detail="User registration failed")


def db_get_user(user_id: int):
    """사용자 정보 조회"""
    query = "SELECT id, name, email, created_at, expired_at, profile FROM users WHERE id = %s"
    user = fetch_one(query, (user_id,))

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "created_at": user["created_at"],
        "expired_at": user["expired_at"],
        "profile": user["profile"],
    }
