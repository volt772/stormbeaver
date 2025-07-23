import os
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2 import pool
from dotenv import load_dotenv
from pathlib import Path


# ✅ 환경 변수 자동 감지 (기본값: development)
env_mode = os.getenv("ENV", "development")
env_file = f"/home/volt772/work/source/stormbeaver/.env.{env_mode}"

# ✅ 해당 .env 파일이 존재하지 않으면 기본 .env 파일 사용
if not Path(env_file).exists():
    env_file = "/home/volt772/work/source/stormbeaver/.env"

load_dotenv(env_file)  # ✅ .env 파일 로드

# ✅ PostgreSQL Connection Pool 생성
DATABASE_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
}

# ✅ 최소 1개 ~ 최대 10개의 커넥션 풀 생성
db_pool = psycopg2.pool.SimpleConnectionPool(1, 10, **DATABASE_CONFIG)


# ✅ DB 연결을 가져오는 함수
def get_db():
    conn = db_pool.getconn()
    try:
        yield conn
    finally:
        db_pool.putconn(conn)  # ✅ 사용한 연결 반환


# ✅ 단일 결과를 가져오는 함수
def fetch_one(query, params=None):
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, params or ())
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        db_pool.putconn(conn)


# ✅ 다수의 결과를 가져오는 함수
def fetch_multi(query, params=None):
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, params or ())
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    finally:
        db_pool.putconn(conn)


# ✅ INSERT, UPDATE, DELETE 실행 함수 (RETURNING 값 옵션 추가)
def execute(query, params=None, returning=False):
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, params or ())
            conn.commit()
            if returning:
                result = cursor.fetchone()
                return dict(result) if result else None
            return cursor.rowcount
    finally:
        db_pool.putconn(conn)


# ✅ 애플리케이션 종료 시 모든 연결 닫기
def close_db_pool():
    db_pool.closeall()
