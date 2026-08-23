import logging

logger = logging.getLogger("uvicorn")

async def send_verification_email(email: str, code: str) -> bool:
    """
    سرویس موقت ارسال ایمیل برای محیط توسعه (کد را در کنسول چاپ می‌کند)
    """
    logger.info(f"========== [MOCK EMAIL SERVICE] ==========")
    logger.info(f"To: {email}")
    logger.info(f"Verification Code: {code}")
    logger.info(f"===========================================")
    return True