from fastapi import APIRouter, Path
from pydantic import BaseModel
from typing import Optional
from database.validators import validate_user_id
from models.jobs import db_get_jobs, db_add_job, db_update_job, db_delete_job

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


# 채용 등록 모델
class JobCreateRequest(BaseModel):
    id: str
    user_id: int
    company: str
    url: str
    region: str
    status_id: int
    apply_date: int  # 타임스탬프 형식 (밀리초 단위)
    deadline: int
    route_id: int
    memo: Optional[str]  # 🔹 선택적 필드 (값이 없을 수도 있음)


# 채용 수정 모델
class JobUpdateRequest(BaseModel):
    user_id: int
    company: str
    url: str
    region: str
    status_id: int
    apply_date: int  # 타임스탬프 형식 (밀리초 단위)
    deadline: int
    route_id: int
    memo: Optional[str]


@router.get("/{user_id}")
def handle_get_jobs(user_id: int = Path(..., description="사용자 ID")):
    """사용자의 채용 관련 데이터 조회"""

    # 1️⃣ `user_id` 검증
    validate_user_id(user_id)

    # 2️⃣ 데이터 조회
    user, statuses, filters, routes, jobs = db_get_jobs(user_id)

    # 3️⃣ JSON 응답 구성
    return {
        "user": {
            "id": user["id"],
        },
        "statuses": [
            {"id": s["id"], "name": s["name"], "color": s["color"]} for s in statuses
        ],
        "filters": [
            {
                "id": f["id"],
                "user_id": f["user_id"],
                "name": f["name"],
                "value": f["value"],
            }
            for f in filters
        ],
        "routes": [
            {
                "id": r["id"],
                "user_id": r["user_id"],
                "name": r["name"],
                "color": r["color"],
            }
            for r in routes
        ],
        "jobs": [
            {
                "id": j["id"],
                "user_id": j["user_id"],
                "company": j["company"],
                "url": j["url"],
                "region": j["region"],
                "status_id": j["status_id"],
                "apply_date": j["apply_date"],
                "deadline": j["deadline"],
                "route_id": j["route_id"],
                "memo": j["memo"],
            }
            for j in jobs
        ],
    }


@router.post("")
def handle_add_job(job: JobCreateRequest):
    """새로운 채용 정보를 추가하고 상세 정보 반환"""

    # 1️⃣ `user_id` 검증
    validate_user_id(job.user_id)

    # 2️⃣ `add_job()` 호출
    created_job = db_add_job(job)

    if not created_job:
        raise HTTPException(status_code=500, detail="Failed to insert job")

    return {
        "seq_id": created_job["seq_id"],
        "id": created_job["id"],
        "user_id": created_job["user_id"],
        "company": created_job["company"],
        "url": created_job["url"],
        "region": created_job["region"],
        "status_id": created_job["status_id"],
        "apply_date": created_job["apply_date"],
        "deadline": created_job["deadline"],
        "route_id": created_job["route_id"],
        "memo": created_job["memo"],
        "status_name": created_job["status_name"],
        "status_color": created_job["status_color"],
        "route_name": created_job["route_name"],
        "route_color": created_job["route_color"],
    }


@router.put("/{job_id}")
def handle_update_job(job_id: str, job: JobUpdateRequest):
    """기존 채용 정보 업데이트"""

    # 1️⃣ `user_id` 검증
    validate_user_id(job.user_id)

    # 2️⃣ `update_job()` 호출
    updated_job = db_update_job(job_id, job)

    if not updated_job:
        raise HTTPException(status_code=500, detail="Failed to update job")

    return {
        "seq_id": updated_job["seq_id"],
        "id": updated_job["id"],
        "user_id": updated_job["user_id"],
        "company": updated_job["company"],
        "url": updated_job["url"],
        "region": updated_job["region"],
        "status_id": updated_job["status_id"],
        "apply_date": updated_job["apply_date"],
        "deadline": updated_job["deadline"],
        "route_id": updated_job["route_id"],
        "memo": updated_job["memo"],
        "status_name": updated_job["status_name"],
        "status_color": updated_job["status_color"],
        "route_name": updated_job["route_name"],
        "route_color": updated_job["route_color"],
    }


@router.delete("/{job_id}/{user_id}")
def handle_delete_job(
    job_id: str = Path(..., description="삭제할 채용 정보 ID"),
    user_id: int = Path(..., description="사용자 ID"),
):
    """채용 정보 삭제"""

    # 1️⃣ `user_id` 검증
    validate_user_id(user_id)

    # 2️⃣ `delete_job()` 호출
    deleted_job_id = db_delete_job(job_id)

    return {"id": deleted_job_id}
