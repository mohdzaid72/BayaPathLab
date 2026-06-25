from sqlalchemy import Column, Integer, String, Text,DateTime, Float, Boolean
from sqlalchemy.sql import func
from database import Base
import os
from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
class TestPoster(Base):
    __tablename__ = "test_posters"
    
    id = Column(Integer, primary_key=True, index=True)

    test_name = Column(String(100), nullable=False)

    price = Column(Float, nullable=False)

    # NEW FIELD
    mrp_price = Column(Float, nullable=True)

    description = Column(Text)

    image_path = Column(String(255), nullable=False)

    created_at = Column(
    DateTime,
    default=lambda: datetime.now(IST)
    )

    is_active = Column(Boolean, default=True)
class Enquiry(Base):
    __tablename__ = "enquiries"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String(100), nullable=False)
    phone = Column(String(15), nullable=False)
    email = Column(String(100))
    test_name = Column(String(100))
    message = Column(Text)
    created_at = Column(
    DateTime,
    default=lambda: datetime.now(IST)
)

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    
    
class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, nullable=False)
    admin_id = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False)