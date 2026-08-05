import httpx
from datetime import date, datetime
from app.core.config import settings

TIMER_API_URL = "https://api.time.ir/v1/convert"

async def shamsi_to_gregorian(jalali_str: str) -> date | None:
    """تبدیل تاریخ شمسی به میلادی با API"""
    if not jalali_str:
        return None
    
    parts = str(jalali_str).split('-')
    if len(parts) != 3:
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                TIMER_API_URL,
                params={
                    "type": "jalali",
                    "year": int(parts[0]),
                    "month": int(parts[1]),
                    "day": int(parts[2])
                }
            )
            if response.status_code == 200:
                data = response.json()
                g = data.get("gregorian", {})
                return date(g.get("year", 2025), g.get("month", 1), g.get("day", 1))
    except:
        # اگر API در دسترس نبود، تبدیل تقریبی
        pass
    
    # تبدیل تقریبی (fallback)
    return approx_jalali_to_greg(jalali_str)

def approx_jalali_to_greg(jalali_str: str) -> date:
    """تبدیل تقریبی شمسی به میلادی (بدون API)"""
    import jdatetime
    parts = str(jalali_str).split('-')
    if len(parts) == 3:
        jd = jdatetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
        return jd.togregorian()
    return date.today()

async def gregorian_to_shamsi(greg_date: date) -> str:
    """تبدیل تاریخ میلادی به شمسی با API"""
    if not greg_date:
        return ""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                TIMER_API_URL,
                params={
                    "type": "gregorian",
                    "year": greg_date.year,
                    "month": greg_date.month,
                    "day": greg_date.day
                }
            )
            if response.status_code == 200:
                data = response.json()
                j = data.get("jalali", {})
                return f"{j.get('year', 1405)}-{j.get('month', 1):02d}-{j.get('day', 1):02d}"
    except:
        pass
    
    # تبدیل تقریبی
    import jdatetime
    jd = jdatetime.date.fromgregorian(date=greg_date)
    return f"{jd.year}-{jd.month:02d}-{jd.day:02d}"