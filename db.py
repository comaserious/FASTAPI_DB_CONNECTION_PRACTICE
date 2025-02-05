# 기본 config
DB_USER = "postgres"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = "5432"
DATABASE_NAME = "db_test"

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker , declarative_base
from typing import AsyncGenerator

# 비동기 데이터베이스 URL (asyncpg 드라이버 사용)
DATABASE_URL_ASYNC = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DATABASE_NAME}"

# 1. 데이터베이스가 존재하지 않을 경우 자동 생성하는 동기 함수
def create_database_if_not_exists():
    default_database = "postgres"
    default_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{default_database}"
    # AUTOCOMMIT 모드로 엔진 생성 (CREATE DATABASE 명령은 트랜잭션 외부에서 실행되어야 함)
    engine_sync = create_engine(default_url, isolation_level="AUTOCOMMIT")
    with engine_sync.connect() as conn:
        result = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
            {"dbname": DATABASE_NAME}
        )
        exists = result.scalar() is not None
        if not exists:
            conn.execute(text(f"CREATE DATABASE {DATABASE_NAME}"))
            print(f"Database '{DATABASE_NAME}' created.")
        else:
            print(f"Database '{DATABASE_NAME}' already exists.")


# 비동기 엔진 생성
engine = create_async_engine(
    DATABASE_URL_ASYNC,
    echo=True,              # SQL 로그 출력 (개발/디버깅 시 유용)
    pool_size=10,           # 기본 풀에 유지할 연결의 수
    # max_overflow=20,        # 기본 풀을 초과하여 생성할 수 있는 최대 연결 수
    # pool_timeout=30,        # 사용 가능한 연결이 없을 경우 대기할 최대 시간(초)
    # pool_recycle=1800,      # 일정 시간 이후 연결을 재생성하여 stale connection 방지
    # pool_pre_ping=True      # 연결 유효성 검사로 비정상 연결 제거
)

# 비동기 세션 생성 팩토리
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# 베이스 클래스 생성
Base = declarative_base()

# 비동기 세션 의존성 함수
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        # async with 구문으로 인해 세션은 자동으로 종료됨