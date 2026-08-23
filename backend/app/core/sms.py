import logging

logger = logging.getLogger("uvicorn")

async def send_verification_sms(phone: str, code: str) -> bool:
    """
    سرویس موقت ارسال پیامک برای محیط توسعه (کد را در کنسول چاپ می‌کند)
    """
    logger.info(f"=========== [MOCK SMS SERVICE] ===========")
    logger.info(f"To: {phone}")
    logger.info(f"Verification Code: {code}")
    logger.info(f"===========================================")
    return True