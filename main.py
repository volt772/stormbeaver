from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers import users, jobs, filters, routes, settings
from database.database_connection import close_db_pool


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 중에는 모든 도메인 허용 (배포 시 수정)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 각 라우터 포함
app.include_router(users.router)
app.include_router(jobs.router)
app.include_router(filters.router)
app.include_router(routes.router)
app.include_router(settings.router)


@app.on_event("shutdown")
def shutdown_db_pool():
    print("🔻 서버 종료: DB 커넥션 풀 정리")
    close_db_pool()


# FastAPI 실행
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5300, reload=True)
