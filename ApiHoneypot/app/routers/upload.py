from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import UPLOAD_DIR, MAX_UPLOAD_SIZE, ALLOWED_CONTENT_TYPES
from app.security import get_current_user
import os
import uuid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(oauth2_scheme)]
)
async def upload_file(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}"
        )

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Max upload size is {MAX_UPLOAD_SIZE // (1024*1024)} MB"
        )

    orig_name = os.path.basename(file.filename)
    ext = os.path.splitext(orig_name)[1]
    safe_name = f"{uuid.uuid4().hex}{ext}"

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    dest = os.path.join(UPLOAD_DIR, safe_name)

    with open(dest, "wb") as f:
        f.write(contents)

    return {
        "filename": safe_name,
        "original_name": orig_name,
        "content_type": file.content_type,
        "size": len(contents),
        "path": dest
    }
