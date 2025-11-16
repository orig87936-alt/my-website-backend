"""
图片上传路由
提供图片上传功能，仅管理员可访问
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from ..utils.dependencies import require_admin
import os
import uuid
from pathlib import Path
import shutil
from typing import Dict

router = APIRouter(prefix="/api/v1/upload", tags=["upload"])

# 上传目录配置
UPLOAD_DIR = Path("uploads/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# 最大文件大小：5MB
MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post("/image", response_model=Dict[str, str])
async def upload_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_admin)
) -> Dict[str, str]:
    """
    上传图片文件
    
    - **file**: 图片文件（JPG, PNG, WebP）
    - **返回**: {"url": "图片URL"}
    - **权限**: 仅管理员
    """
    
    # 验证文件是否存在
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # 验证文件类型
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # 读取文件内容
    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")
    
    # 验证文件大小
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # 验证文件不为空
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    
    # 生成唯一文件名
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # 保存文件
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # 返回文件URL（相对路径）
    file_url = f"/uploads/images/{unique_filename}"
    
    return {"url": file_url}


@router.delete("/image", response_model=Dict[str, str])
async def delete_image(
    url: str,
    current_user: dict = Depends(require_admin)
) -> Dict[str, str]:
    """
    删除图片文件
    
    - **url**: 图片URL（例如：/uploads/images/xxx.jpg）
    - **返回**: {"message": "Image deleted successfully"}
    - **权限**: 仅管理员
    """
    
    # 从URL提取文件名
    if not url.startswith("/uploads/images/"):
        raise HTTPException(status_code=400, detail="Invalid image URL")
    
    filename = url.replace("/uploads/images/", "")
    file_path = UPLOAD_DIR / filename
    
    # 检查文件是否存在
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    # 删除文件
    try:
        file_path.unlink()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")
    
    return {"message": "Image deleted successfully"}

