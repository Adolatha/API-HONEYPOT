from fastapi import APIRouter, Depends, status, HTTPException, Body, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import AsyncSessionLocal
from app.models import Post
from app.schemas import PostCreate, PostOut, PostUpdate
from app.security import get_current_user

router = APIRouter(prefix="/posts", tags=["posts"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_in: PostCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    new_post = Post(
        author_id=current_user.id,
        title=post_in.title.strip(),
        body=post_in.body.strip()
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post

@router.get("/", response_model=list[PostOut])
async def list_posts(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(Post).order_by(Post.created_at.desc()))
    posts = result.scalars().all()
    return posts

@router.get("/{post_id}", response_model=PostOut)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.patch(
    "/{post_id}",
    response_model=PostOut,
    status_code=status.HTTP_200_OK,
)
async def update_post(
    post_in: PostUpdate = Body(...),
    post_id: int = Path(..., description="ID of the post to edit"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to edit this post")

    if post_in.title is not None:
        post.title = post_in.title.strip()
    if post_in.body is not None:
        post.body = post_in.body.strip()

    await db.commit()
    await db.refresh(post)
    return post
