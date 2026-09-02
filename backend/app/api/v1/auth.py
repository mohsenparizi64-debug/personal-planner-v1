from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from datetime import datetime, timedelta
import secrets
import re
from pydantic import BaseModel

from app.schemas.user import (
    UserCreate, UserRead, Token, LoginRequest, UserUpdate,
    SendOTPRequest, VerifyAndRegisterRequest
)
from app.crud.user import (
    get_user_by_email, create_user, authenticate_user, 
    update_user, generate_password_reset_token, reset_password
)
from app.core.security import create_access_token, verify_password
from app.core.email import send_verification_email
from app.core.sms import send_verification_sms
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.all_models import User

# جدول اعتبارسنجی موقت کد‌های ۶ رقمی
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.db.base import Base, TimestampMixin

class AuthVerification(Base, TimestampMixin):
    __tablename__ = "auth_verifications"
    id = Column(Integer, primary_key=True, index=True)
    target = Column(String, index=True, nullable=False)
    verification_type = Column(String, default="email")
    code = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    attempts = Column(Integer, default=0)
    is_used = Column(Boolean, default=False)

router = APIRouter()

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# تابع تبدیل ارقام فارسی و عربی به انگلیسی در بک‌اند
def to_english_digits(s: str) -> str:
    if not s:
        return ""
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    res = ""
    for char in str(s).strip():
        if char in persian_digits:
            res += str(persian_digits.index(char))
        elif char in arabic_digits:
            res += str(arabic_digits.index(char))
        else:
            res += char
    return res.strip()

# 🔍 جستجوی کاربر با ایمیل یا شماره تماس (با نرمال‌سازی کامل)
async def get_user_by_identifier(db: AsyncSession, identifier: str):
    clean_id = to_english_digits(identifier).lower()
    res = await db.execute(
        select(User).where(
            or_(User.email == clean_id, User.phone == clean_id)
        )
    )
    return res.scalar_one_or_none()

# 🛡️ ۱. ارسال کد تأیید ۶ رقمی
@router.post("/send-otp")
async def send_registration_otp(data: SendOTPRequest, db: AsyncSession = Depends(get_db)):
    if data.honeypot:
        return {"message": "کد تأیید ارسال شد", "expires_in_seconds": 180}

    target = to_english_digits(data.target)
    is_sms = (data.type == "sms")

    if is_sms:
        if not re.match(r"^09\d{9}$", target):
            raise HTTPException(status_code=400, detail="شماره موبایل نامعتبر است. نمونه صحیح: 09123456789")
    else:
        if "@" not in target or "." not in target:
            raise HTTPException(status_code=400, detail="آدرس ایمیل نامعتبر است.")

    existing_user = await get_user_by_identifier(db, target)
    if existing_user:
        target_name = "شماره موبایل" if is_sms else "ایمیل"
        raise HTTPException(
            status_code=400, 
            detail=f"این {target_name} قبلاً در سیستم ثبت شده است. لطفاً وارد شوید."
        )

    now = datetime.utcnow()

    recent_res = await db.execute(
        select(AuthVerification)
        .where(
            AuthVerification.target == target,
            AuthVerification.created_at >= now - timedelta(seconds=60),
            AuthVerification.is_used == False
        )
    )
    if recent_res.scalar_one_or_none():
        raise HTTPException(
            status_code=429, 
            detail="کد تأیید اخیراً ارسال شده است. لطفاً ۶۰ ثانیه صبر کرده و مجدداً تلاش کنید."
        )

    old_res = await db.execute(
        select(AuthVerification).where(AuthVerification.target == target)
    )
    for old_entry in old_res.scalars().all():
        old_entry.is_used = True

    otp_code = f"{secrets.randbelow(900000) + 100000}"
    expires_at = now + timedelta(minutes=3)

    verification_entry = AuthVerification(
        target=target,
        verification_type="sms" if is_sms else "email",
        code=otp_code,
        expires_at=expires_at,
        attempts=0,
        is_used=False
    )
    db.add(verification_entry)
    await db.commit()

    if is_sms:
        await send_verification_sms(target, otp_code)
        msg = f"کد تأیید به شماره {target} پیامک شد."
    else:
        await send_verification_email(target, otp_code)
        msg = f"کد تأیید به ایمیل {target} ارسال شد."

    return {
        "message": msg,
        "expires_in_seconds": 180
    }

# 🛡️ ۲. تأیید کد ۶ رقمی و ساخت اکانت با ورود مستقیم
@router.post("/verify-and-register", response_model=Token)
async def verify_and_register(data: VerifyAndRegisterRequest, db: AsyncSession = Depends(get_db)):
    if data.honeypot:
        raise HTTPException(status_code=400, detail="درخواست نامعتبر است.")

    target = to_english_digits(data.target)
    code = to_english_digits(data.code)
    password = to_english_digits(data.password)
    is_sms = (data.type == "sms")

    existing_user = await get_user_by_identifier(db, target)
    if existing_user:
        raise HTTPException(status_code=400, detail="این کاربر قبلاً ثبت‌نام کرده است.")

    now = datetime.utcnow()

    otp_res = await db.execute(
        select(AuthVerification)
        .where(
            AuthVerification.target == target,
            AuthVerification.is_used == False,
            AuthVerification.expires_at > now
        )
        .order_by(AuthVerification.created_at.desc())
    )
    otp_entry = otp_res.scalar_one_or_none()

    if not otp_entry:
        raise HTTPException(
            status_code=400, 
            detail="کد تأیید منقضی شده یا درخواستی یافت نشد. لطفاً مجدداً درخواست کد دهید."
        )

    if otp_entry.attempts >= 5:
        otp_entry.is_used = True
        await db.commit()
        raise HTTPException(status_code=400, detail="تعداد تلاش‌های مجاز به پایان رسید. لطفاً مجدداً کد دریافت کنید.")

    if otp_entry.code.strip() != code.strip():
        otp_entry.attempts += 1
        await db.commit()
        raise HTTPException(status_code=400, detail=f"کد وارد شده اشتباه است ({5 - otp_entry.attempts} تلاش باقیمانده).")

    otp_entry.is_used = True

    email_val = None if is_sms else target
    phone_val = target if is_sms else None

    user = await create_user(
        db=db, 
        email=email_val or f"{phone_val}@mobile.local", 
        password=password, 
        full_name=data.full_name, 
        phone=phone_val
    )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# 🔑 ۳. ورود دوگانه با ایمیل یا شماره موبایل (با تبدیل خودکار ارقام فارسی)
@router.post("/login", response_model=Token)
async def login(user_in: LoginRequest, db: AsyncSession = Depends(get_db)):
    clean_identifier = to_english_digits(user_in.email)
    clean_password = to_english_digits(user_in.password)

    user = await get_user_by_identifier(db, clean_identifier)
    if not user or not verify_password(clean_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="ایمیل/شماره موبایل یا کلمه عبور اشتباه است.")

    # 🧠 اگر «مرا بخاطر بسپار» فعال باشد، توکن ۷ روزه صادر می‌شود
    # در غیر این صورت از مقدار پیش‌فرض settings (۱ ساعت) استفاده می‌شود
    if user_in.remember_me:
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(days=7)
        )
    else:
        access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserRead)
async def update_me(data: UserUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = await update_user(db, current_user.id, data.model_dump(exclude_unset=True))
    return user

@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    token = await generate_password_reset_token(db, data.email)
    if not token:
        raise HTTPException(status_code=404, detail="کاربری با این شناسه یافت نشد.")
    return {"message": "Reset token generated", "token": token}

@router.post("/reset-password")
async def reset_password_endpoint(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    success = await reset_password(db, data.token, data.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="توکن بازنشانی نامعتبر یا منقضی شده است.")
    return {"message": "کلمه عبور با موفقیت تغییر کرد."}