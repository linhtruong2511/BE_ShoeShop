import os
import shutil
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.core.dependencies import get_current_admin
from app.schemas.base import BaseResponse
from app.models.user import User
router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=BaseResponse)
async def upload_image(
    file: UploadFile = File(...),
    admin: User = Depends(get_current_admin)
):
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    file_extension = file.filename.split(".")[-1] if file.filename else "jpg"
    file_name = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not upload file")

    return BaseResponse(data={"file_url": f"/{UPLOAD_DIR}/{file_name}"})
