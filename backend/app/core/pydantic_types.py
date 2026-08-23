"""نوع Pydantic سفارشی برای پذیرش تاریخ شمسی و میلادی و تبدیل خودکار به میلادی."""
from datetime import date
from typing import Optional, Annotated, Any

from pydantic_core import core_schema

from app.core.date_utils import to_gregorian_date


class GregorianDate:
    """Pydantic نوع سفارشی: هر دو تاریخ شمسی و میلادی را می‌پذیرد
    و همیشه یک datetime.date میلادی برمی‌گرداند."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.any_schema(),   # اول هر چیزی را بپذیر
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, value):
        if value is None or value == "":
            return None
        if isinstance(value, date):
            return value

        g = to_gregorian_date(value)   # تشخیص خودکار شمسی/میلادی
        if g is None:
            raise ValueError(
                f"فرمت تاریخ نامعتبر است: {value!r} — باید شمسی یا میلادی باشد"
            )
        return g


# نوع آماده استفاده: GDate = تاریخ اختیاری شمسی/میلادی
GDate = Annotated[Optional[date], GregorianDate]