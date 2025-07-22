from database.database_connection import fetch_multi, fetch_one, execute
from fastapi import HTTPException


def db_get_routes(user_id: int):
    """사용자의 routes + 기본 admin(1) routes 조회"""
    query = (
        "SELECT id, user_id, name, color FROM route WHERE user_id = 1 OR user_id = %s"
    )
    routes = fetch_multi(query, (user_id,))

    if not routes:
        raise HTTPException(status_code=404, detail="No routes found")

    return [
        {
            "id": route["id"],
            "user_id": route["user_id"],
            "name": route["name"],
            "color": route["color"],
        }
        for route in routes
    ]


def db_add_route(user_id: int, name: str, color: str):
    """새로운 route 추가 후 ID 반환"""
    insert_query = """
        INSERT INTO route (user_id, name, color)
        VALUES (%s, %s, %s) RETURNING id;
    """
    new_route_id = execute(
        query=insert_query,
        params=(user_id, name, color),
        returning=True,
    )

    if not new_route_id:
        raise HTTPException(status_code=500, detail="Failed to insert route")

    return new_route_id["id"]


def db_update_route(route_id: int, user_id: int, name: str, color: str):
    """기존 route 정보 업데이트"""
    update_query = """
        UPDATE route SET name = %s, color = %s 
        WHERE id = %s AND user_id = %s
        RETURNING id;
    """
    updated_route_id = execute(
        query=update_query,
        params=(name, color, route_id, user_id),
        returning=True,
    )

    if not updated_route_id:
        raise HTTPException(
            status_code=404, detail="Route not found or no changes made"
        )

    return updated_route_id["id"]


def db_delete_route(route_id: int, user_id: int):
    """기존 route 삭제"""
    delete_query = "DELETE FROM route WHERE id = %s AND user_id = %s RETURNING id;"
    deleted_route_id = execute(
        query=delete_query,
        params=(route_id, user_id),
        returning=True,
    )

    if not deleted_route_id:
        raise HTTPException(
            status_code=404, detail="Route not found or already deleted"
        )

    return deleted_route_id["id"]
