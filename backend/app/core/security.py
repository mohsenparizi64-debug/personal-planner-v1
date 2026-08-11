import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import JWTError, jwt
from app.core.config import settings

ALGORITHM = "HS256"

# --- ۱. الگوریتم هشینگ امن PBKDF2 با نمک تصادفی ---

def get_password_hash(password: str) -> str:
    """تولید هش امن با 100,000 بار تکرار و نمک تصادفی"""
    salt = os.urandom(16)
    iterations = 100000
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """بررسی صحت رمز عبور (پشتیبانی از الگوریتم جدید PBKDF2 و قدیمی SHA256)"""
    if not hashed_password:
        return False

    # پشتیبانی از رمزهای قدیمی SHA256 ساده
    if not hashed_password.startswith("pbkdf2_sha256$"):
        legacy_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
        return legacy_hash == hashed_password

    # بررسی رمز با الگوریتم جدید PBKDF2
    try:
        parts = hashed_password.split("$")
        if len(parts) != 4:
            return False
        
        _, iterations_str, salt_hex, hash_hex = parts
        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
        
        key = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, iterations)
        return key.hex() == hash_hex
    except Exception:
        return False

# --- ۲. توابع مدیریت توکن‌های JWT ---

def create_access_token(subject: Any = None, expires_delta: Optional[timedelta] = None, data: Optional[dict] = None) -> str:
    """ساخت توکن دسترسی (استخراج هوشمند شناسه کاربر از هر نوع ورودی)"""
    raw = subject if subject is not None else data
    
    # اگر ورودی دیکشنری بود، آن‌قدر لایه‌ها را باز کن تا به شناسه اصلی برسد
    while isinstance(raw, dict):
        raw = raw.get("sub")
        
    sub_str = str(raw) if raw is not None else ""
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode = {"exp": expire, "sub": sub_str}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    """رمزگشایی و اعتبارسنجی توکن دسترسی"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def generate_password_reset_token(email: str) -> str:
    """ساخت توکن برای بازیابی رمز عبور"""
    delta = timedelta(hours=1)
    now = datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt

def verify_password_reset_token(token: str) -> Optional[str]:
    """اعتبارسنجی توکن بازیابی رمز عبور"""
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token["sub"]
    except JWTError:
        return None