from database.database_connection import fetch_one, fetch_multi, execute
from fastapi import HTTPException


def db_get_setting(user_id: int, key: str):
    """사용자의 특정 설정값 조회"""
    query = "SELECT value FROM settings WHERE user_id = %s AND key = %s"
    params = (user_id, key)
    setting = fetch_one(query, params)

    if setting:
        return {"value": setting["value"]}
    else:
        raise HTTPException(status_code=404, detail="Setting not found")


def db_get_all_settings(user_id: int):
    """사용자의 모든 설정값 조회"""
    query = "SELECT key, value FROM settings WHERE user_id = %s"
    params = (user_id,)
    settings = fetch_multi(query, params)

    if settings:
        return {s["key"]: s["value"] for s in settings}  # ✅ 모든 설정을 JSON 형식으로 반환
    else:
        raise HTTPException(status_code=404, detail="No settings found")


def db_add_setting(user_id: int, key: str, value: str):
    """환경 설정 저장 (UPSERT 방식)"""

    # 1️⃣ 기존 설정 존재 여부 확인
    select_query = "SELECT id FROM settings WHERE user_id = %s AND key = %s"
    existing_setting = fetch_one(select_query, (user_id, key))

    if existing_setting:
        # 2️⃣ 기존 설정 업데이트
        update_query = """
            UPDATE settings 
            SET value = %s
            WHERE user_id = %s AND key = %s
            RETURNING id
        """
        updated_setting_id = execute(
            update_query, (value, user_id, key), returning=True
        )
        return {"setting_id": updated_setting_id["id"]}

    else:
        # 3️⃣ 새로운 설정 삽입
        insert_query = """
            INSERT INTO settings (user_id, key, value) 
            VALUES (%s, %s, %s)
            RETURNING id
        """
        new_setting_id = execute(insert_query, (user_id, key, value), returning=True)

        if new_setting_id:
            return {"setting_id": new_setting_id["id"]}
        else:
            raise HTTPException(status_code=500, detail="Failed to save setting")
