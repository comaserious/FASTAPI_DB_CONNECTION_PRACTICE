from pydantic import BaseModel

# Pydantic 모델 정의 (요청/응답 검증용)
class UserCreate(BaseModel):
    name: str
    email: str

class UserUpdate(BaseModel):
    name: str = None
    email: str = None