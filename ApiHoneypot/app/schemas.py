# app/schemas.py
from pydantic import BaseModel, EmailStr, constr
from datetime import datetime
from typing import Optional, List
from typing import Optional

class UserCreate(BaseModel):
    name: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8, max_length=128)

class UserUpdate(BaseModel):
    name: Optional[constr(min_length=3, max_length=50)] = None
    email: Optional[EmailStr] = None
    password: Optional[constr(min_length=8, max_length=128)] = None

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None

class PostCreate(BaseModel):
    title: constr(min_length=1, max_length=200)
    body: constr(min_length=1, max_length=5000)

class PostUpdate(BaseModel):
    title: Optional[constr(min_length=1, max_length=200)] = None
    body: Optional[constr(min_length=1, max_length=5000)] = None

class PostOut(BaseModel):
    id: int
    author_id: int
    title: str
    body: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class CommentCreate(BaseModel):
    body: constr(min_length=1, max_length=2000)

class CommentUpdate(BaseModel):
    body: Optional[constr(min_length=1, max_length=2000)] = None

class CommentOut(BaseModel):
    id: int
    post_id: int
    author_id: int
    body: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
