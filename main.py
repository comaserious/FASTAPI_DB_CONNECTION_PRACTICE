from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models import *
from db import AsyncSession, get_db, create_database_if_not_exists
from sqlalchemy import select
from table_models import *
from asyncio import to_thread
from db_operation import execute_query

# lifespan 이벤트 핸들러 정의
@asynccontextmanager
async def lifespan(app: FastAPI):
    await to_thread(create_database_if_not_exists)  # 동기 함수 호출을 별도 스레드로 offload
    await init_db()
    yield
    # 종료 시 클린업 작업을 추가할 수 있음

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/users/", response_model=dict)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # 동일 이메일 존재 여부 확인
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar_one_or_none()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"id": new_user.id, "name": new_user.name, "email": new_user.email}

# 엔드포인트: 사용자 조회
@app.get("/users/{user_id}", response_model=dict)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "name": user.name, "email": user.email}
    # return {"user" : user , "result" : result}

# 엔드포인트: 사용자 업데이트
@app.put("/users/{user_id}", response_model=dict)
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_update.name is not None:
        user.name = user_update.name
    if user_update.email is not None:
        user.email = user_update.email
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "name": user.name, "email": user.email}

# 엔드포인트: 사용자 삭제
@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
    return {"detail": f"User with id {user_id} deleted"}

@app.get("/query/{user_id}")
async def select_query(user_id : int, db: AsyncSession = Depends(get_db)):
    print(f"/query/{user_id} reached")
    query = "SELECT * FROM users where id = :user_id"
    params = {"user_id" : user_id}

    result = await execute_query(db, query, params)

    return result

@app.get("/test")
async def test(db: AsyncSession = Depends(get_db)):
    query = "SELECT * FROM users"
    result = await execute_query(db, query) 
    user = result.fetchall()[0]

    return {"id" : user.id , "name" : user.name , "email" : user.email}
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
