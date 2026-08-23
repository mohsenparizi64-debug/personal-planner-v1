from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Literal

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

class UserRead(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: str
    password: str

# 🛡️ اسکیمای درخواست ارسال کد OTP
class SendOTPRequest(BaseModel):
    target: str
    type: Literal["sms", "email"] = "sms"
    honeypot: Optional[str] = None

# 🛡️ اسکیمای تأیید کد و تکمیل ثبت‌نام
class VerifyAndRegisterRequest(BaseModel):
    target: str
    code: str
    password: str
    full_name: Optional[str] = None
    type: Literal["sms", "email"] = "sms"
    honeypot: Optional[str] = None