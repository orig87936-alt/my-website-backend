"""
Appointment model
"""
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Text, Date, Integer, DateTime, CheckConstraint, Index, UniqueConstraint, text
from app.models.base import Base
from app.models.types import UUID


class Appointment(Base):
    """Appointment booking model with time slot management"""
    
    __tablename__ = "appointments"
    
    # Primary key
    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User information
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    
    # Appointment details
    appointment_date = Column(Date, nullable=False, index=True)
    time_slot = Column(String(10), nullable=False)  # Format: HH:MM
    service_type = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Status tracking
    status = Column(String(20), nullable=False, default="pending", server_default="pending", index=True)
    
    # Email notification tracking
    notification_status = Column(String(20), nullable=False, default="pending", server_default="pending")
    notification_retry_count = Column(Integer, nullable=False, default=0, server_default="0")
    notification_last_attempt = Column(DateTime(timezone=True), nullable=True)
    
    # Confirmation
    confirmation_number = Column(String(20), unique=True, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'confirmed', 'completed', 'cancelled')",
            name="valid_status"
        ),
        CheckConstraint(
            "notification_status IN ('pending', 'sent', 'failed')",
            name="valid_notification_status"
        ),
        # Prevent double-booking: unique index on date+time for non-cancelled appointments
        Index(
            "idx_unique_appointment_slot",
            "appointment_date", "time_slot",
            unique=True
        ),
        # Index for failed notification retry processing
        Index(
            "idx_appointments_notification_retry",
            "notification_status", "notification_retry_count"
        ),
    )
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, name='{self.name}', date={self.appointment_date}, time={self.time_slot}, status='{self.status}')>"

