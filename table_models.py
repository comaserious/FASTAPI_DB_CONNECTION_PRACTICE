from db import Base, engine
from sqlalchemy import Column, Integer, String, text
from pgvector.sqlalchemy import Vector

# 모델 정의 (예: users 테이블)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    embedding = Column(Vector(1536))


async def init_db():
    async with engine.begin() as conn:
        # 대상 데이터베이스에서 pgvector 확장을 생성 (이미 존재하면 아무 영향 없이 넘어감)
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        # 테이블 생성
        await conn.run_sync(Base.metadata.create_all)
    print("Tables and extensions created.")