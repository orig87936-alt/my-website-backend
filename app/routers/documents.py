"""
文档上传路由
提供文档上传、解析和历史记录功能
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form, Query
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from pathlib import Path
import time
from datetime import datetime

from ..database import get_db
from ..core.deps import require_admin
from ..models.document import DocumentUpload
from ..models.user import User
from ..schemas.document import (
    UploadDocumentResponse,
    DocumentUploadHistoryResponse,
    DocumentUploadDetail,
    ParseResult,
    ParseMetadata,
    UploadedImage
)
from ..schemas.article import ContentBlock
from ..services.document_parser import parse_document, upload_images_concurrently
from ..services.metadata_generator import MetadataGenerator
from ..services.translation import TranslationService

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

# HTTP Bearer token security scheme
security = HTTPBearer()

# 文件大小限制：10MB
MAX_FILE_SIZE = 10 * 1024 * 1024

# 允许的文件类型
ALLOWED_EXTENSIONS = {".md", ".docx"}


@router.post(
    "/upload",
    response_model=UploadDocumentResponse,
    summary="Upload and parse document",
    description="T075: Upload Markdown/Word document with automatic parsing, image extraction, and AI metadata generation"
)
async def upload_document(
    file: UploadFile = File(..., description="Document file (.md or .docx, max 10MB)"),
    category: Optional[str] = Form(None, description="Article category (optional)"),
    auto_translate: bool = Form(False, description="Auto-translate content to target language"),
    target_lang: str = Form("en", description="Target language for translation (zh/en)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UploadDocumentResponse:
    """
    Upload and parse Markdown or Word document with intelligent content extraction.

    **Features:**
    - **Document Parsing**: Supports .md and .docx files (T035-T040)
    - **Image Extraction**: Automatically extracts and uploads images (max 5 concurrent) (T039)
    - **AI Metadata Generation**: Auto-generates summary, category, and tags (T041-T044)
    - **Auto Translation**: Optional translation to target language (T049)
    - **Security**: Content sanitization and XSS protection (T073)
    - **Performance**: File size validation and streaming (T072)

    **Workflow:**
    1. Upload document file
    2. Parse content and extract images
    3. Upload images concurrently (max 5 at a time)
    4. Generate AI metadata (summary, category, tags)
    5. Optionally translate content
    6. Return structured content blocks ready for article creation

    **Parameters:**
    - **file**: Document file (.md or .docx, max 10MB)
    - **category**: Article category (optional, will be AI-suggested if not provided)
    - **auto_translate**: Enable automatic translation (default: false)
    - **target_lang**: Target language for translation (zh/en, default: en)

    **File Size Limit:** 10MB

    **Allowed File Types:** .md, .docx

    **Permissions:** Admin only

    **Returns:**
    - **upload_id**: Unique upload identifier
    - **filename**: Original filename
    - **file_type**: File extension
    - **file_size**: File size in bytes
    - **upload_status**: Upload status (success/failed)
    - **parse_result**: Parsed content including:
      - **title**: Extracted document title
      - **content_blocks**: Structured content blocks
      - **images**: Uploaded images with URLs
      - **metadata**: AI-generated summary, category, and tags
    - **uploaded_at**: Upload timestamp
    """
    start_time = time.time()

    # 验证文件名
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
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")
    
    # 验证文件大小
    file_size = len(file_content)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    
    # 创建上传记录
    upload_record = DocumentUpload(
        filename=file.filename,
        file_type=file_ext[1:],  # 移除点号
        file_size=file_size,
        upload_status='processing',
        created_by=current_user.username
    )
    
    try:
        # 1. 解析文档
        parse_result = parse_document(file_content, file.filename)
        content_blocks = parse_result['content_blocks']
        metadata = parse_result['metadata']
        images = parse_result['images']
        
        # 2. 上传图片（如果有）
        uploaded_images = []
        if images:
            # 获取认证 token - 从 credentials 获取
            auth_token = credentials.credentials
            uploaded_images = await upload_images_concurrently(images, auth_token, max_concurrent=5)
        
        # 3. 生成 AI 元数据
        metadata_generator = MetadataGenerator()
        
        # 提取纯文本内容
        plain_text = '\n\n'.join([block.content for block in content_blocks if block.content])
        
        # 生成元数据
        ai_metadata = await metadata_generator.generate_all_metadata(
            title=metadata.get('title', file.filename),
            content=plain_text,
            language='zh'
        )
        
        # 合并元数据
        final_title = metadata.get('title', file.filename)
        final_summary = ai_metadata.get('summary', metadata.get('summary', ''))
        final_category = category or ai_metadata.get('category', 'headline')
        final_tags = ai_metadata.get('tags', [])
        
        # 4. 翻译（如果需要）
        content_en = None
        title_en = None
        summary_en = None
        translation_time = None

        if auto_translate:
            translation_start = time.time()
            translation_service = TranslationService(db)

            # 翻译标题和摘要
            try:
                title_result = await translation_service.translate_text(
                    text=final_title,
                    source_lang='zh',
                    target_lang=target_lang
                )
                title_en = title_result['translated_text']
            except Exception as e:
                print(f"⚠️ Title translation failed: {e}")
                title_en = final_title

            try:
                summary_result = await translation_service.translate_text(
                    text=final_summary,
                    source_lang='zh',
                    target_lang=target_lang
                )
                summary_en = summary_result['translated_text']
            except Exception as e:
                print(f"⚠️ Summary translation failed: {e}")
                summary_en = final_summary

            # 翻译所有文本块
            translated_blocks = []
            for i, block in enumerate(content_blocks):
                if block.type in ['paragraph', 'heading', 'quote', 'list'] and block.content:
                    try:
                        translation_result = await translation_service.translate_text(
                            text=block.content,
                            source_lang='zh',
                            target_lang=target_lang
                        )
                        # 提取翻译后的文本
                        translated_text = translation_result['translated_text']

                        translated_blocks.append(ContentBlock(
                            type=block.type,
                            content=translated_text,
                            level=block.level,
                            language=block.language,
                            caption=block.caption
                        ))
                    except Exception as e:
                        # 翻译失败时保留原文
                        print(f"⚠️ Translation failed for block {i+1}: {e}")
                        translated_blocks.append(block)
                else:
                    # 非文本块（如图片、代码）直接复制
                    translated_blocks.append(block)

            content_en = translated_blocks
            translation_time = time.time() - translation_start
        
        # 5. 构建解析结果
        parse_metadata = ParseMetadata(
            word_count=metadata.get('word_count', 0),
            paragraph_count=metadata.get('paragraph_count', 0),
            image_count=len(uploaded_images),
            parse_time=metadata.get('parse_time', 0),
            translation_time=translation_time
        )
        
        parse_result_schema = ParseResult(
            title=final_title,
            title_en=title_en,
            summary=final_summary,
            summary_en=summary_en,
            category=final_category,
            tags=final_tags,
            content_zh=content_blocks,
            content_en=content_en,
            images_uploaded=[
                UploadedImage(
                    original_name=img['original_name'],
                    uploaded_url=img['uploaded_url'],
                    size=img['size']
                ) for img in uploaded_images if 'error' not in img
            ],
            metadata=parse_metadata
        )
        
        # 6. 更新上传记录
        upload_record.upload_status = 'success'
        upload_record.parse_result = parse_result_schema.model_dump()
        
        db.add(upload_record)
        await db.commit()
        await db.refresh(upload_record)
        
        # 7. 返回响应
        return UploadDocumentResponse(
            upload_id=str(upload_record.id),
            filename=upload_record.filename,
            file_type=upload_record.file_type,
            file_size=upload_record.file_size,
            parse_result=parse_result_schema,
            status='success',
            created_at=upload_record.created_at
        )
        
    except Exception as e:
        # 更新上传记录为失败
        upload_record.upload_status = 'failed'
        upload_record.error_message = str(e)
        
        db.add(upload_record)
        await db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}"
        )


@router.get("/history", response_model=DocumentUploadHistoryResponse)
async def get_upload_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> DocumentUploadHistoryResponse:
    """
    获取文档上传历史记录
    
    - **limit**: 返回数量（默认 20，最大 100）
    - **offset**: 偏移量（默认 0）
    - **status**: 过滤状态（success/failed）
    - **权限**: 仅管理员
    """
    from sqlalchemy import select, func
    
    # 构建查询
    query = select(DocumentUpload).order_by(DocumentUpload.created_at.desc())
    
    # 过滤状态
    if status:
        query = query.where(DocumentUpload.upload_status == status)
    
    # 获取总数
    count_query = select(func.count()).select_from(DocumentUpload)
    if status:
        count_query = count_query.where(DocumentUpload.upload_status == status)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页查询
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return DocumentUploadHistoryResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/{upload_id}", response_model=DocumentUploadDetail)
async def get_upload_detail(
    upload_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> DocumentUploadDetail:
    """
    获取特定上传的详细信息
    
    - **upload_id**: 上传 ID
    - **权限**: 仅管理员
    """
    from sqlalchemy import select
    from uuid import UUID
    
    try:
        upload_uuid = UUID(upload_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid upload ID format")
    
    query = select(DocumentUpload).where(DocumentUpload.id == upload_uuid)
    result = await db.execute(query)
    upload = result.scalar_one_or_none()
    
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    return DocumentUploadDetail.model_validate(upload)

