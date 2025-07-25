from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers import weather
from database.database_connection import close_db_pool

app = FastAPI(root_path="/weather-api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 중에는 모든 도메인 허용 (배포 시 수정)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 각 라우터 포함
app.include_router(weather.router)


@app.on_event("shutdown")
def shutdown_db_pool():
    print("🔻 서버 종료: DB 커넥션 풀 정리")
    close_db_pool()


# FastAPI 실행
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5532, reload=True)
