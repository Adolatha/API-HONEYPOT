# app/routers/account.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import User             
from app.schemas import UserUpdate, UserOut
from app.utils import hash_password
from app.security import  get_current_user

router = APIRouter(prefix="/account", tags=["account"])

@router.get("/", response_model=UserOut)
async def read_account(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/", response_model=UserOut)
async def update_account(
    user_in: UserUpdate,
    current_user: User     = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db)  
):
    
    if user_in.name and user_in.name != current_user.name:
        q = select(User).where(User.name == user_in.name)
        if (await db.execute(q)).scalars().first():
            raise HTTPException(status_code=400, detail="Username already in use")
        current_user.name = user_in.name.strip()

    if user_in.email and user_in.email != current_user.email:
        q = select(User).where(User.email == user_in.email)
        if (await db.execute(q)).scalars().first():
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = user_in.email.lower().strip()

    if user_in.password:
        current_user.hashed_password = hash_password(user_in.password)

    await db.commit()
    await db.refresh(current_user)
    return current_user
