from database.database_connection import fetch_multi, fetch_one, execute
from fastapi import HTTPException


def db_get_filters(user_id: int):
    """
    특정 사용자의 필터 목록을 조회하고, status 테이블의 모든 데이터를 반환합니다.
    """

    # status 테이블 조회
    status_query = "SELECT id, name, color FROM status;"
    status_rows = fetch_multi(status_query)

    # filtering 테이블 조회 (조건: user_id)
    filtering_query = (
        "SELECT id, user_id, name, value FROM filtering WHERE user_id = %s;"
    )
    filtering_rows = fetch_multi(filtering_query, (user_id,))

    return {
        "statuses": [
            {"id": row["id"], "name": row["name"], "color": row["color"]}
            for row in status_rows
        ],
        "filtering": [
            {
                "id": row["id"],
                "user_id": row["user_id"],
                "name": row["name"],
                "value": row["value"],
            }
            for row in filtering_rows
        ],
    }


def db_add_filter(user_id: int, name: str, value: str):
    """새 필터 추가 후 ID 반환"""
    insert_query = """
        INSERT INTO filtering (user_id, name, value)
        VALUES (%s, %s, %s)
        RETURNING id;
    """
    new_filter_id = execute(
        query=insert_query,
        params=(user_id, name, value),
        returning=True,
    )

    if not new_filter_id:
        raise HTTPException(status_code=500, detail="Failed to insert filter")

    return new_filter_id["id"]


def db_update_filter(filter_id: int, user_id: int, name: str, value: str):
    """기존 필터 정보 업데이트"""
    update_query = """
        UPDATE filtering 
        SET name = %s, value = %s
        WHERE id = %s AND user_id = %s
        RETURNING id;
    """
    updated_filter_id = execute(
        query=update_query,
        params=(name, value, filter_id, user_id),
        returning=True,
    )

    if not updated_filter_id:
        raise HTTPException(
            status_code=404, detail="Filter not found or no changes made"
        )

    return updated_filter_id["id"]


def db_delete_filter(filter_id: int, user_id: int):
    """기존 필터 삭제"""
    delete_query = "DELETE FROM filtering WHERE id = %s AND user_id = %s RETURNING id;"
    deleted_filter_id = execute(
        query=delete_query,
        params=(filter_id, user_id),
        returning=True,
    )

    if not deleted_filter_id:
        raise HTTPException(
            status_code=404, detail="Filter not found or already deleted"
        )

    return deleted_filter_id["id"]
