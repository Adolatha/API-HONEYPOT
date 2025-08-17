from fastapi import FastAPI
from starlette.responses import RedirectResponse
from app.db import init_db
from app.db_decoy import init_decoy_db
from app.routers import register, auth, posts, comments, account, upload, decoy_db
import os
from app.config import UPLOAD_DIR

app = FastAPI(
    title="API + Honeypot",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.on_event("startup")
async def on_startup():
    await init_db()
    await init_decoy_db()

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/api/docs")

app.include_router(register.router, prefix="/api")
app.include_router(auth.router,     prefix="/api")
app.include_router(posts.router,    prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(account.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(decoy_db.router, prefix="/webhoneypot")




