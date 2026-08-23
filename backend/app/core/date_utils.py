"""ابزار استانداردسازی تاریخ: شمسی <-> میلادی.
استاندارد ذخیره‌سازی: میلادی ISO-8601 (YYYY-MM-DD)
"""
from datetime import date, datetime
from typing import Optional
import jdatetime

# تشخیص بر اساس محدوده سال
SHAMSI_MIN = 1300
SHAMSI_MAX = 1499
GREG_MIN = 1900
GREG_MAX = 2100


def is_valid_iso(s: str) -> bool:
    """آیا رشته یک تاریخ میلادی معتبر YYYY-MM-DD است؟"""
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def normalize_separators(s: str) -> str:
    """همه جداکننده‌ها (/ , . -) را به - تبدیل می‌کند."""
    if not s or not isinstance(s, str):
        return s
    return s.replace("/", "-").replace(".", "-").replace(" ", "-")


def parse_year_parts(s: str) -> Optional[tuple[int, int, int]]:
    s = normalize_separators(s).strip()
    parts = s.split("-")
    if len(parts) != 3:
        return None
    try:
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return None
    if m < 1 or m > 12 or d < 1 or d > 31:
        return None
    return y, m, d


def detect_calendar(year: int) -> str:
    """تشخیص اینکه سال متعلق به شمسی است یا میلادی."""
    if SHAMSI_MIN <= year <= SHAMSI_MAX:
        return "shamsi"
    if GREG_MIN <= year <= GREG_MAX:
        return "gregorian"
    # بازه مبهم -> پیش‌فرض شمسی (اپ فارسی)
    return "shamsi"


def to_gregorian_iso(s: str) -> Optional[str]:
    """ورودی شمسی یا میلادی را به ISO میلادی تبدیل می‌کند."""
    parts = parse_year_parts(s)
    if parts is None:
        return None
    y, m, d = parts
    cal = detect_calendar(y)
    try:
        if cal == "shamsi":
            g = jdatetime.date(y, m, d).togregorian()
            return g.isoformat()
        # میلادی
        g = date(y, m, d)
        return g.isoformat()
    except (ValueError, OverflowError):
        return None


def to_shamsi_display(iso_str: str) -> Optional[str]:
    """ISO میلادی -> رشته نمایشی شمسی (YYYY/MM/DD)."""
    if not is_valid_iso(iso_str):
        return None
    y, m, d = map(int, iso_str.split("-"))
    j = jdatetime.date.fromgregorian(year=y, month=m, day=d)
    return f"{j.year}/{j.month:02d}/{j.day:02d}"


def today_gregorian_iso() -> str:
    return date.today().isoformat()


def now_gregorian_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def gregorian_iso_to_date(iso_str) -> Optional[date]:
    """ISO 'YYYY-MM-DD' یا شیء date -> date. خطاها را None می‌کند."""
    if iso_str is None:
        return None
    if isinstance(iso_str, date):
        return iso_str
    if not is_valid_iso(str(iso_str)):
        return None
    y, m, d = map(int, str(iso_str).split("-"))
    return date(y, m, d)


def to_gregorian_date(value) -> Optional[date]:
    """ورودی شمسی/میلادی (str یا date) -> شیء date میلادی. تشخیص خودکار تقویم."""
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value  # از قبل میلادی Date است
    iso = to_gregorian_iso(str(value))   # تابع موجود
    return gregorian_iso_to_date(iso)


def add_months(d: date, months: int) -> date:
    """افزودن تعداد ماه واقعی (با مدیریت پایان ماه)."""
    month_index = d.year * 12 + (d.month - 1) + months
    year = month_index // 12
    month = (month_index % 12) + 1
    day = min(d.day, _days_in_month(year, month))
    return date(year, month, day)


def _days_in_month(y: int, m: int) -> int:
    if m == 2:
        leap = (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)
        return 29 if leap else 28
    return 30 if m in (4, 6, 9, 11) else 31