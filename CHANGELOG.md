# گزارش تغییرات (Changelog)

تمام تغییرات مهم پروژه `personal-planner-v1` در این فایل ثبت می‌شود.

## [Unreleased] - 2026-09-01

### اضافه شد (Added)

**ماژول مهارت‌ها (Skills):**
- مدل `Skill` با فیلدهای جدید: `start_date`, `last_practiced`, `level`, `source_url`, `target_hours`, `practiced_hours`
- مدل `LearningLog.duration_minutes` برای محاسبه streak
- مدل `MentorReport` با محدودیت ۱ گزارش در روز
- ۶ endpoint جدید: GET/PUT/DELETE skill by_id، /_logs (CRUD کامل)، /_stats/summary
- Schemas: SkillStats (شامل total, mastered, in_progress, streak, hours, by_category)
- Pydantic validator برای فیلد `goal_id` (پشتیبانی از 'independent' یا عدد)
- Migration: `add_mentor_reports_table.py`
- ستون‌های جدید به جدول skills (ALTER TABLE)

**داشبورد:**
- کارت مهارت‌ها در داشبورد با ۴ KPI (کل، streak، پیشرفت، مستقل)
- نمودار میله‌ای Stacked با تفکیک تسک‌های ثابت (بنفش) و دوره‌ای (سبز)
- دو دماسنج عمودی جایگزین دونات ۳بعدی ناواضح
- popup هوشمند روزانه با موقعیت‌یابی ضد بیرون‌زدگی
- گزارش منتور: ۲ پاراگراف با لحن مشوقانه
- Modal تمام‌اسکرین گزارش با دکمه کپی و دانلود `.txt`
- کش Context چت AI در سشن (کاهش ۷۰٪ مصرف توکن)

**فرانت‌اند:**
- دیتا پیکر شمسی `DateInputPersian` با Teleport به body و مرکز viewport
- دسته‌بندی مهارت به صورت select (نه datalist)
- گزینه «مستقل (بدون هدف)» در فرم مهارت
- Timeline ماهانه برای لاگ‌ها
- KPI stats در SkillsPage (۶ کارت)
- فیلتر پیشرفته (دسته‌بندی، وضعیت، هدف، جستجو)
- نمایش تاریخ شمسی در همه جا (تبدیل خودکار شمسی → میلادی قبل از ارسال)
- دکمه‌های ویرایش/حذف/ثبت یادداشت روی هر کارت مهارت

### تغییر یافت (Changed)

- بازنویسی کامل متغیرهای CSS تم‌های ۲۰۲۶ (روشن و تیره)
- حذف کلاس‌های تیره هاردکد در `App.vue` (رفع مشکل تم روشن)
- افزایش کنتراست متن زیرعنوان در `LoginPage.vue`
- `mentor.py`: استفاده از کش context برای کاهش ۷۰٪ توکن
- `dashboard.py`: محاسبه دقیق هفته شمسی از شنبه تا جمعه

### رفع شد (Fixed)

- **route conflict FastAPI:** `/{skill_id}: int` با `/_logs` match می‌شد و 422 می‌داد. تغییر path به `/by_id/{skill_id}` و `/_logs`
- **MissingGreenlet** در `crud_skill`: رفع با `selectinload(Skill.learning_logs)`
- **overlap popup تقویم با مودال:** مودال Skills دارای `overflow-y-auto` بود و popup absolute را clip می‌کرد. حل با Teleport به body
- **عدم تطابق شمارش تسک روزانه:** ایجاد تابع جامع `_is_completed_on_day` در dashboard.py
- **تاری و بیضی شدن نمودار دونات:** حذف و جایگزینی با دماسنج
- **نقطه طلایی ثابت روز جاری:** حذف (روی سه‌شنبه فیکس می‌ماند)
- **تاریخ میلادی در popup داشبورد:** تبدیل به شمسی با `formatDate()`

## نسخه‌های قبلی

برای تاریخچه کامل تغییرات به `git log` مراجعه کنید.
