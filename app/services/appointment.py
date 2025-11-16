"""
Appointment service for business logic
"""
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from uuid import UUID
import uuid

from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, TimeSlot


class AppointmentService:
    """Service for appointment management"""
    
    # 工作时间配置 (9:00 - 18:00, 30分钟间隔)
    WORK_START_HOUR = 9
    WORK_END_HOUR = 18
    SLOT_INTERVAL_MINUTES = 30
    
    @staticmethod
    def generate_confirmation_number() -> str:
        """生成预约确认号"""
        now = datetime.now()
        # 格式: APT + YYYYMMDD + 随机3位数
        import random
        random_suffix = random.randint(100, 999)
        return f"APT{now.strftime('%Y%m%d')}{random_suffix}"
    
    @staticmethod
    async def create_appointment(
        db: AsyncSession,
        appointment_data: AppointmentCreate
    ) -> Appointment:
        """
        创建新预约
        
        Args:
            db: Database session
            appointment_data: Appointment creation data
            
        Returns:
            Created appointment
            
        Raises:
            ValueError: If time slot is already booked
        """
        # 检查时间槽是否已被预约
        is_available = await AppointmentService.check_slot_availability(
            db,
            appointment_data.appointment_date,
            appointment_data.time_slot
        )
        
        if not is_available:
            raise ValueError(f"时间槽 {appointment_data.appointment_date} {appointment_data.time_slot} 已被预约")
        
        # 生成确认号
        confirmation_number = AppointmentService.generate_confirmation_number()
        
        # 创建预约
        appointment = Appointment(
            id=str(uuid.uuid4()),  # Generate new UUID
            name=appointment_data.name,
            email=appointment_data.email,
            phone=appointment_data.phone,
            appointment_date=appointment_data.appointment_date,
            time_slot=appointment_data.time_slot,
            service_type=appointment_data.service_type,
            notes=appointment_data.notes,
            status="pending",
            confirmation_number=confirmation_number,
            notification_status="pending",
            notification_retry_count=0
        )
        
        db.add(appointment)
        await db.commit()
        await db.refresh(appointment)
        
        return appointment
    
    @staticmethod
    async def get_appointment_by_id(
        db: AsyncSession,
        appointment_id: str
    ) -> Optional[Appointment]:
        """获取单个预约"""
        result = await db.execute(
            select(Appointment).where(Appointment.id == appointment_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_appointments(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Tuple[List[Appointment], int]:
        """
        获取预约列表（分页）
        
        Args:
            db: Database session
            page: Page number (1-based)
            page_size: Number of items per page
            status: Filter by status
            start_date: Filter by start date
            end_date: Filter by end date
            
        Returns:
            Tuple of (appointments list, total count)
        """
        # Build query
        query = select(Appointment)
        count_query = select(func.count()).select_from(Appointment)
        
        # Apply filters
        filters = []
        if status:
            filters.append(Appointment.status == status)
        if start_date:
            filters.append(Appointment.appointment_date >= start_date)
        if end_date:
            filters.append(Appointment.appointment_date <= end_date)
        
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(Appointment.appointment_date.desc(), Appointment.time_slot.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await db.execute(query)
        appointments = result.scalars().all()
        
        return list(appointments), total
    
    @staticmethod
    async def update_appointment(
        db: AsyncSession,
        appointment_id: str,
        appointment_data: AppointmentUpdate
    ) -> Optional[Appointment]:
        """更新预约（管理员）"""
        appointment = await AppointmentService.get_appointment_by_id(db, appointment_id)
        if not appointment:
            return None
        
        # Update fields
        update_data = appointment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(appointment, field, value)
        
        appointment.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(appointment)
        
        return appointment
    
    @staticmethod
    async def check_slot_availability(
        db: AsyncSession,
        appointment_date: date,
        time_slot: str
    ) -> bool:
        """
        检查时间槽是否可用
        
        Args:
            db: Database session
            appointment_date: Date to check
            time_slot: Time slot to check (HH:MM)
            
        Returns:
            True if available, False if booked
        """
        result = await db.execute(
            select(Appointment).where(
                and_(
                    Appointment.appointment_date == appointment_date,
                    Appointment.time_slot == time_slot,
                    Appointment.status.in_(['pending', 'confirmed'])  # 排除已取消的预约
                )
            )
        )
        existing = result.scalar_one_or_none()
        return existing is None
    
    @staticmethod
    async def get_available_slots(
        db: AsyncSession,
        appointment_date: date
    ) -> List[TimeSlot]:
        """
        获取指定日期的所有可用时间槽
        
        Args:
            db: Database session
            appointment_date: Date to check
            
        Returns:
            List of time slots with availability status
        """
        # 生成所有可能的时间槽
        slots = []
        current_hour = AppointmentService.WORK_START_HOUR
        current_minute = 0
        
        while current_hour < AppointmentService.WORK_END_HOUR:
            time_str = f"{current_hour:02d}:{current_minute:02d}"
            slots.append(time_str)
            
            # 增加30分钟
            current_minute += AppointmentService.SLOT_INTERVAL_MINUTES
            if current_minute >= 60:
                current_minute = 0
                current_hour += 1
        
        # 查询已预约的时间槽
        result = await db.execute(
            select(Appointment.time_slot).where(
                and_(
                    Appointment.appointment_date == appointment_date,
                    Appointment.status.in_(['pending', 'confirmed'])
                )
            )
        )
        booked_slots = set(row[0] for row in result.fetchall())
        
        # 构建响应
        time_slots = [
            TimeSlot(time=slot, available=slot not in booked_slots)
            for slot in slots
        ]
        
        return time_slots
    
    @staticmethod
    async def update_notification_status(
        db: AsyncSession,
        appointment_id: str,
        status: str,
        increment_retry: bool = False
    ) -> Optional[Appointment]:
        """
        更新通知状态
        
        Args:
            db: Database session
            appointment_id: Appointment ID
            status: New notification status ('pending', 'sent', 'failed')
            increment_retry: Whether to increment retry count
            
        Returns:
            Updated appointment or None
        """
        appointment = await AppointmentService.get_appointment_by_id(db, appointment_id)
        if not appointment:
            return None
        
        appointment.notification_status = status
        appointment.notification_last_attempt = datetime.utcnow()
        
        if increment_retry:
            appointment.notification_retry_count += 1
        
        await db.commit()
        await db.refresh(appointment)
        
        return appointment
    
    @staticmethod
    async def get_pending_notifications(
        db: AsyncSession,
        max_retry_count: int = 3
    ) -> List[Appointment]:
        """
        获取待发送或需要重试的通知
        
        Args:
            db: Database session
            max_retry_count: Maximum retry count
            
        Returns:
            List of appointments needing notification
        """
        result = await db.execute(
            select(Appointment).where(
                or_(
                    # 新预约，待发送
                    Appointment.notification_status == 'pending',
                    # 发送失败，未超过重试次数
                    and_(
                        Appointment.notification_status == 'failed',
                        Appointment.notification_retry_count < max_retry_count
                    )
                )
            ).order_by(Appointment.created_at.asc())
        )
        
        return list(result.scalars().all())

