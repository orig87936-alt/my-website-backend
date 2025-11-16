"""
Appointment API endpoints
"""
import asyncio
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentListResponse,
    AppointmentConfirmation,
    AvailableSlotsResponse
)
from app.services.appointment import AppointmentService
from app.services.email import EmailService
from app.core.deps import require_admin
from app.models.user import User

router = APIRouter(prefix="/appointments", tags=["appointments"])

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)


async def send_confirmation_email_task(appointment: AppointmentResponse):
    """后台任务：发送确认邮件"""
    try:
        success = await EmailService.send_appointment_confirmation(
            to_email=appointment.email,
            name=appointment.name,
            confirmation_number=appointment.confirmation_number,
            appointment_date=str(appointment.appointment_date),
            time_slot=appointment.time_slot,
            service_type=appointment.service_type,
            notes=appointment.notes
        )
        
        # 这里可以更新通知状态（需要 db session）
        # 为了简化，我们在创建时已经设置为 pending
        print(f"📧 确认邮件发送{'成功' if success else '失败'}: {appointment.email}")
        
    except Exception as e:
        print(f"❌ 发送确认邮件异常: {str(e)}")


@router.post("", response_model=AppointmentConfirmation, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/hour")  # Max 10 appointments per hour per IP
async def create_appointment(
    request: Request,
    appointment_data: AppointmentCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新预约（公开接口）
    
    - 验证表单数据
    - 检查时间槽可用性
    - 保存预约到数据库
    - 异步发送确认邮件
    """
    try:
        # 创建预约
        appointment = await AppointmentService.create_appointment(db, appointment_data)
        
        # 转换为响应模型
        appointment_response = AppointmentResponse.model_validate(appointment)
        
        # 添加后台任务发送邮件
        background_tasks.add_task(send_confirmation_email_task, appointment_response)
        
        return AppointmentConfirmation(
            success=True,
            message="预约成功！确认邮件将发送至您的邮箱。",
            appointment=appointment_response
        )
        
    except ValueError as e:
        # 时间槽冲突
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建预约失败: {str(e)}"
        )


@router.get("", response_model=AppointmentListResponse)
async def get_appointments(
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    获取预约列表（管理员）
    
    - 支持分页
    - 支持按状态过滤
    - 支持按日期范围过滤
    """
    appointments, total = await AppointmentService.get_appointments(
        db=db,
        page=page,
        page_size=page_size,
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return AppointmentListResponse(
        items=[AppointmentResponse.model_validate(apt) for apt in appointments],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/available-slots", response_model=AvailableSlotsResponse)
async def get_available_slots(
    appointment_date: date,
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定日期的可用时间槽（公开接口）
    
    - 返回所有时间槽及其可用状态
    - 用于前端显示可选时间
    """
    slots = await AppointmentService.get_available_slots(db, appointment_date)
    
    return AvailableSlotsResponse(
        date=appointment_date,
        slots=slots
    )


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取单个预约详情（公开接口）
    
    - 用户可以通过确认号查看自己的预约
    """
    appointment = await AppointmentService.get_appointment_by_id(db, appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    return AppointmentResponse.model_validate(appointment)


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: str,
    appointment_data: AppointmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    更新预约状态（管理员）
    
    - 更新预约状态（pending, confirmed, completed, cancelled）
    - 更新备注信息
    """
    appointment = await AppointmentService.update_appointment(
        db=db,
        appointment_id=appointment_id,
        appointment_data=appointment_data
    )
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    return AppointmentResponse.model_validate(appointment)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment(
    appointment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    取消预约（管理员）
    
    - 将预约状态设置为 cancelled
    """
    appointment = await AppointmentService.update_appointment(
        db=db,
        appointment_id=appointment_id,
        appointment_data=AppointmentUpdate(status="cancelled")
    )
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    return None

