from db import Base, engine
from sqlalchemy import Column, Integer, String

# 모델 정의 (예: users 테이블)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)


# 비동기 DB 초기화: 테이블 생성
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("DB initialized")