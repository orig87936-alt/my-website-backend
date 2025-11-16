"""
Appointment schemas for request/response validation
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID


class AppointmentBase(BaseModel):
    """Base appointment schema"""
    name: str = Field(..., min_length=1, max_length=100, description="预约人姓名")
    email: EmailStr = Field(..., description="联系邮箱")
    phone: Optional[str] = Field(None, max_length=50, description="联系电话")
    appointment_date: date = Field(..., description="预约日期")
    time_slot: str = Field(..., pattern=r'^\d{2}:\d{2}$', description="预约时间槽 (格式: HH:MM)")
    service_type: Optional[str] = Field(None, max_length=100, description="服务类型")
    notes: Optional[str] = Field(None, description="备注信息")
    
    @field_validator('appointment_date')
    @classmethod
    def validate_appointment_date(cls, v):
        """验证预约日期不能是过去的日期"""
        if v < date.today():
            raise ValueError("预约日期不能是过去的日期")
        return v
    
    @field_validator('time_slot')
    @classmethod
    def validate_time_slot(cls, v):
        """验证时间槽格式和有效性"""
        try:
            hour, minute = map(int, v.split(':'))
            if not (0 <= hour < 24 and 0 <= minute < 60):
                raise ValueError("时间槽格式无效")
            # 验证是否为30分钟间隔
            if minute not in [0, 30]:
                raise ValueError("时间槽必须是整点或半点 (00 或 30)")
        except (ValueError, AttributeError):
            raise ValueError("时间槽格式必须为 HH:MM")
        return v


class AppointmentCreate(AppointmentBase):
    """创建预约请求模型"""
    pass


class AppointmentUpdate(BaseModel):
    """更新预约请求模型 (管理员)"""
    status: Optional[str] = Field(None, description="预约状态")
    notes: Optional[str] = Field(None, description="备注信息")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """验证状态值"""
        if v is not None:
            allowed_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
            if v not in allowed_statuses:
                raise ValueError(f"状态必须是以下之一: {', '.join(allowed_statuses)}")
        return v


class AppointmentResponse(BaseModel):
    """预约响应模型 - 不继承 AppointmentBase 以避免日期验证"""
    id: UUID
    name: str
    email: EmailStr
    phone: Optional[str]
    appointment_date: date
    time_slot: str
    service_type: Optional[str]
    notes: Optional[str]
    status: str
    confirmation_number: Optional[str]
    notification_status: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "张三",
                "email": "zhangsan@example.com",
                "phone": "13800138000",
                "appointment_date": "2025-11-15",
                "time_slot": "14:00",
                "service_type": "咨询服务",
                "notes": "希望了解产品详情",
                "status": "pending",
                "confirmation_number": "APT20251108001",
                "notification_status": "sent",
                "created_at": "2025-11-08T10:30:00Z",
                "updated_at": "2025-11-08T10:30:00Z"
            }
        }
    }


class AppointmentListResponse(BaseModel):
    """预约列表响应模型"""
    items: List[AppointmentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [],
                "total": 50,
                "page": 1,
                "page_size": 10,
                "total_pages": 5
            }
        }
    }


class TimeSlot(BaseModel):
    """时间槽模型"""
    time: str = Field(..., description="时间 (HH:MM)")
    available: bool = Field(..., description="是否可用")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "time": "14:00",
                "available": True
            }
        }
    }


class AvailableSlotsResponse(BaseModel):
    """可用时间槽响应模型"""
    date: date
    slots: List[TimeSlot]
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2025-11-15",
                "slots": [
                    {"time": "09:00", "available": True},
                    {"time": "09:30", "available": True},
                    {"time": "10:00", "available": False},
                    {"time": "10:30", "available": True}
                ]
            }
        }
    }


class AppointmentConfirmation(BaseModel):
    """预约确认响应模型"""
    success: bool
    message: str
    appointment: AppointmentResponse
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "预约成功！确认邮件将发送至您的邮箱。",
                "appointment": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "张三",
                    "email": "zhangsan@example.com",
                    "confirmation_number": "APT20251108001",
                    "appointment_date": "2025-11-15",
                    "time_slot": "14:00",
                    "status": "pending"
                }
            }
        }
    }

