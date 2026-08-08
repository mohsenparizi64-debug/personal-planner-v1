// ابزار تاریخ شمسی/میلادی — سمت فرانت
import * as jalaali from 'jalaali-js';

export const SHAMSI_MIN = 1300;
export const SHAMSI_MAX = 1499;
export const GREG_MIN = 1900;
export const GREG_MAX = 2100;

export function normalizeSeparators(s) {
  if (!s) return s;
  return String(s).replaceAll('/', '-').replaceAll('.', '-').replaceAll(' ', '-').trim();
}

export function parseYearParts(s) {
  const clean = normalizeSeparators(s);
  const parts = clean.split('-');
  if (parts.length !== 3) return null;
  const y = Number(parts[0]);
  const m = Number(parts[1]);
  const d = Number(parts[2]);
  if (!y || !m || !d || m < 1 || m > 12 || d < 1 || d > 31) return null;
  return { y, m, d };
}

export function detectCalendar(year) {
  if (year >= SHAMSI_MIN && year <= SHAMSI_MAX) return 'shamsi';
  if (year >= GREG_MIN && year <= GREG_MAX) return 'gregorian';
  return 'shamsi'; // پیش‌فرض
}

export function isGregorianISO(s) {
  if (typeof s !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(s)) return false;
  const dt = new Date(s + 'T00:00:00Z');
  return !Number.isNaN(dt.getTime());
}

// تبدیل شمسی -> میلادی ISO
export function toGregorianISO(input) {
  const p = parseYearParts(input);
  if (!p) return null;
  const { y, m, d } = p;
  if (detectCalendar(y) === 'shamsi') {
    if (!jalaali.isValidJalaaliDate(y, m, d)) return null;
    const g = jalaali.toGregorian(y, m, d);
    return `${g.gy}-${String(g.gm).padStart(2, '0')}-${String(g.gd).padStart(2, '0')}`;
  }
  // میلادی
  const dt = new Date(y, m - 1, d);
  if (dt.getFullYear() !== y || dt.getMonth() !== m - 1 || dt.getDate() !== d) return null;
  return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
}

// میلادی ISO -> شمسی نمایشی
export function toShamsiDisplay(isoStr) {
  if (!isGregorianISO(isoStr)) return null;
  const [gy, gm, gd] = isoStr.split('-').map(Number);
  const j = jalaali.toJalaali(gy, gm, gd);
  return `${j.jy}/${String(j.jm).padStart(2, '0')}/${String(j.jd).padStart(2, '0')}`;
}

// تشخیص نوع تاریخ برای نمایش پیام به کاربر
export function detectInputType(input) {
  const p = parseYearParts(input);
  if (!p) return 'invalid';
  return detectCalendar(p.y);
}

// قالب‌بندی برای نمایش: میلادی ISO -> شمسی /، در صورت خالی، خالی برمی‌گرداند
export function formatDate(value) {
  if (!value) return ''
  const s = toShamsiDisplay(value)
  return s || value
}