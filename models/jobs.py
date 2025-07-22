from database.database_connection import fetch_multi, fetch_one, execute
from fastapi import HTTPException
from psycopg2.errors import UniqueViolation, ForeignKeyViolation
from database.validators import validate_status_and_route


def db_get_jobs(user_id: int):
    """사용자의 채용 관련 데이터 조회"""

    # 1️⃣ 사용자 정보 조회
    user_query = "SELECT id FROM users WHERE id = %s;"
    user = fetch_one(user_query, (user_id,))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2️⃣ 상태 목록 조회
    status_query = "SELECT id, name, color FROM status;"
    statuses = fetch_multi(status_query)

    # 3️⃣ 사용자 커스텀 필터 목록 조회
    filter_query = "SELECT id, user_id, name, value FROM filtering WHERE user_id = %s;"
    filters = fetch_multi(filter_query, (user_id,))

    # 4️⃣ 지원 경로 조회 (Admin 데이터 포함)
    route_query = (
        "SELECT id, user_id, name, color FROM route WHERE user_id = 1 OR user_id = %s;"
    )
    routes = fetch_multi(route_query, (user_id,))

    # 5️⃣ 지원 리스트 조회
    jobs_query = """
        SELECT 
            id, 
            user_id,
            company, 
            COALESCE(url, '') AS url, 
            region, 
            status_id, 
            COALESCE(apply_date, 0) AS apply_date, 
            COALESCE(deadline, 0) AS deadline, 
            route_id, 
            COALESCE(memo, '') AS memo
        FROM job_list 
        WHERE user_id = %s
        ORDER BY seq_id DESC;
    """
    jobs = fetch_multi(jobs_query, (user_id,))

    return user, statuses, filters, routes, jobs


def db_add_job(job):
    """새로운 채용 정보를 추가하고 상세 정보 반환"""

    # 1️⃣ `status_id`, `route_id` 검증 (공통 함수 사용)
    validate_status_and_route(job.status_id, job.route_id)

    # 2️⃣ 중복된 `id` 존재 여부 확인
    existing_job_query = "SELECT id FROM job_list WHERE id = %s;"
    existing_job = fetch_one(existing_job_query, (job.id,))

    if existing_job:
        raise HTTPException(status_code=409, detail=f"Job ID '{job.id}' already exists")

    try:
        # 3️⃣ `INSERT` 실행
        insert_query = """
            INSERT INTO job_list (
                id, user_id, company, url, region, status_id, 
                apply_date, deadline, route_id, memo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        execute(
            query=insert_query,
            params=(
                job.id,
                job.user_id,
                job.company,
                job.url,
                job.region,
                job.status_id,
                job.apply_date,
                job.deadline,
                job.route_id,
                job.memo,
            ),
        )
        # 4️⃣ 삽입된 데이터 조회 (JOIN 활용)
        fetch_query = """
            SELECT 
                job_list.seq_id,
                job_list.id,
                job_list.user_id,
                job_list.company,
                job_list.url,
                job_list.region,
                job_list.status_id,
                job_list.apply_date,
                job_list.deadline,
                job_list.route_id,
                job_list.memo,
                status.name AS status_name, 
                status.color AS status_color, 
                route.name AS route_name, 
                route.color AS route_color
            FROM job_list
            LEFT JOIN status ON job_list.status_id = status.id
            LEFT JOIN route ON job_list.route_id = route.id
            WHERE job_list.id = %s;
        """
        inserted_job = fetch_one(fetch_query, (job.id,))

        if not inserted_job:
            raise HTTPException(
                status_code=500, detail="Failed to retrieve inserted job"
            )

        return inserted_job

    except UniqueViolation:
        raise HTTPException(status_code=409, detail=f"Job ID '{job.id}' already exists")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def db_update_job(job_id: str, job):
    """기존 채용 정보 업데이트"""

    # 1️⃣ `status_id`, `route_id` 검증 (공통 함수 사용)
    validate_status_and_route(job.status_id, job.route_id)

    try:
        # 2️⃣ `UPDATE` 실행
        update_query = """
            UPDATE job_list 
            SET company = %s, url = %s, region = %s, status_id = %s, 
                apply_date = %s, deadline = %s, route_id = %s, memo = %s
            WHERE id = %s
            RETURNING id;
        """
        updated_job_id = execute(
            query=update_query,
            params=(
                job.company,
                job.url,
                job.region,
                job.status_id,
                job.apply_date,
                job.deadline,
                job.route_id,
                job.memo,
                job_id,
            ),
            returning=True,
        )

        # 3️⃣ 업데이트 실패 또는 해당 `job_id`가 존재하지 않는 경우
        if not updated_job_id:
            raise HTTPException(
                status_code=404, detail="Job not found or no changes made"
            )

        # 4️⃣ 업데이트된 데이터 조회 (JOIN 활용)
        fetch_query = """
            SELECT 
                job_list.seq_id,
                job_list.id,
                job_list.user_id,
                job_list.company,
                job_list.url,
                job_list.region,
                job_list.status_id,
                job_list.apply_date,
                job_list.deadline,
                job_list.route_id,
                job_list.memo,
                status.name AS status_name, 
                status.color AS status_color, 
                route.name AS route_name, 
                route.color AS route_color
            FROM job_list
            LEFT JOIN status ON job_list.status_id = status.id
            LEFT JOIN route ON job_list.route_id = route.id
            WHERE job_list.id = %s;
        """
        updated_job = fetch_one(fetch_query, (job_id,))

        if not updated_job:
            raise HTTPException(
                status_code=500, detail="Failed to retrieve updated job"
            )

        return updated_job

    except ForeignKeyViolation:
        raise HTTPException(status_code=400, detail="Foreign key constraint violation")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def db_delete_job(job_id: str):
    """채용 정보 삭제"""

    # 1️⃣ `DELETE` 실행
    delete_query = "DELETE FROM job_list WHERE id = %s RETURNING id;"
    deleted_job_id = execute(delete_query, (job_id,), returning=True)

    if not deleted_job_id:
        raise HTTPException(status_code=404, detail="Job not found or already deleted")

    return deleted_job_id["id"]
