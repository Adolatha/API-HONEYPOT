# app/routers/comments.py
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Body
from fastapi import Path


from app.db import get_db
from app.models import Comment, Post
from app.schemas import CommentCreate, CommentOut, CommentUpdate
from app.security import get_current_user

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["comments"])

@router.post("/", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    comment_in: CommentCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    new_comment = Comment(
        post_id=post_id,
        author_id=current_user.id,
        body=comment_in.body.strip()
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment

@router.get("/", response_model=list[CommentOut])
async def list_comments(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at.asc()))
    return result.scalars().all()

@router.patch(
    "/{comment_id}",
    response_model=CommentOut,
    status_code=status.HTTP_200_OK,
)
async def update_comment(
    post_id: int,
    comment_in: CommentUpdate = Body(...),
    comment_id: int = Path(...),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(Comment).where(Comment.id == comment_id, Comment.post_id == post_id)
    )
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to edit this comment")

    if comment_in.body is not None:
        comment.body = comment_in.body.strip()

    await db.commit()
    await db.refresh(comment)
    return comment
