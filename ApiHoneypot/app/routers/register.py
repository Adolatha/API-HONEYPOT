# app/routers/register.py
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import AsyncSessionLocal
from app.models import User
from app.schemas import UserCreate, UserOut
from app.utils import hash_password

router = APIRouter(prefix="/register", tags=["auth"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    query = select(User).where((User.name == user_in.name) | (User.email == user_in.email))
    existing = (await db.execute(query)).scalars().first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already registered")

    hashed_pw = hash_password(user_in.password)
    new_user = User(name=user_in.name, email=user_in.email, hashed_password=hashed_pw)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
