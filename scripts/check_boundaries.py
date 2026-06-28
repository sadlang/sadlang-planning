#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدقّق الحدود لمستودع sadlang-planning (العامّ).

يفرض قواعد GOVERNANCE.md آليًّا على محتوى projects/:
  1. لا أرقام ماليّة (مبالغ بعملات، ميزانيات، تسعير، إيرادات، نسب ربح).
  2. لا أسرار استراتيجيّة مصرَّح بها صراحةً (SECRET/سرّيّ/CONFIDENTIAL).
  3. لا مفاتيح/رموز سرّيّة مسرَّبة (API keys، رموز وصول، JWT، كلمات مرور).

الاستخدام:
    python scripts/check_boundaries.py [مسار]   # افتراضيًّا: projects/

يعيد رمز خروج غير صفريّ عند أيّ مخالفة، ليُفشل CI.
"""
import re
import sys
from pathlib import Path

# اضمن إخراج UTF-8 على كلّ منصّة (Windows console قد يكون cp125x)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

ROOT = Path(__file__).resolve().parent.parent
SCAN_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "projects"

# امتدادات نصّيّة فقط (نتخطّى الصور/PDF الثنائيّة)
TEXT_EXTS = {".md", ".markdown", ".txt", ".yml", ".yaml", ".json", ".csv"}

# عملات وكلمات ماليّة صريحة. نتعمّد التحفّظ لتقليل الإيجابيّات الكاذبة:
# نُطلق فقط عند اقتران رقم بعملة/كلمة ماليّة.
# CURRENCY يغطّي الرموز والأسماء العربيّة والإنجليزيّة الشائعة.
CURRENCY = (
    r"(?:ر\.?س|ريال|دولار|\$|USD|SAR|€|EUR|يورو|درهم|AED|£|GBP|جنيه|"
    r"¥|JPY|CNY|﷼|دينار|KWD|BHD|دج|ل\.س|جنيهًا|بنس|سنت|cent)"
)
# NUM يقبل الأرقام اللاتينيّة (0-9) والعربيّة-الهنديّة (٠-٩) مع فواصل.
NUM = r"[\d٠-٩][\d٠-٩,\.]*"
# نسبة مئويّة (٪/%/«بالمئة/في المئة») مقترنة برقم.
PCT = rf"(?:{NUM}\s*(?:%|٪|بالمئة|بالمائة|في\s+الم[ئا]ة)|(?:%|٪)\s*{NUM})"
# سياق ماليّ يجعل النسبة المئويّة مخالفةً (نتفادى وسم نِسب التقدّم/التغطية البريئة).
PCT_FINANCE_CTX = r"(?:ربح|إيراد|عائد|نمو|هامش|حصة\s+سوق|تسعير|خصم|عمولة|فائدة|ROI|MRR|ARR|margin|revenue|profit)"
FINANCE_PATTERNS = [
    (re.compile(rf"{NUM}\s*{CURRENCY}", re.I), "مبلغ ماليّ مقترن بعملة"),
    (re.compile(rf"{CURRENCY}\s*{NUM}", re.I), "مبلغ ماليّ مقترن بعملة"),
    (re.compile(r"(?:ميزانية|تكلفة|تسعير|سعر|إيراد|ربح(?:ية)?|عائد|ربحيّ?ة|"
                r"budget|cost|pricing|price|revenue|profit|ROI|MRR|ARR)\s*[:：=]?\s*" + NUM, re.I),
     "مؤشّر ماليّ مقترن برقم"),
    (re.compile(rf"{PCT_FINANCE_CTX}.{{0,20}}?{PCT}|{PCT}.{{0,20}}?{PCT_FINANCE_CTX}", re.I),
     "نسبة مئويّة في سياق ماليّ"),
]

# علامات سرّيّة صريحة فقط (لا نخمّن "الاستراتيجية" عمومًا لتفادي الضجيج).
SECRET_PATTERNS = [
    (re.compile(r"\b(?:SECRET|CONFIDENTIAL|INTERNAL[-_ ]ONLY|TOP[-_ ]SECRET|NDA)\b", re.I), "وسم سرّيّ صريح"),
    (re.compile(r"سرّ?ي(?:ّة|ة)?\s+للغاية|محظور\s+النشر|لا\s+تنشر|بالغ\s+السرّيّة", re.I), "إشارة سرّيّة صريحة"),
]

# مفاتيح/رموز/أسرار تقنيّة مسرَّبة. أنماط محدّدة لتقليل الإيجابيّات الكاذبة.
CREDENTIAL_PATTERNS = [
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "مفتاح AWS access key"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), "رمز GitHub"),
    (re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}\b"), "مفتاح API سرّيّ (sk-...)"),
    (re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{6,}\.[A-Za-z0-9_\-]{6,}"), "رمز JWT"),
    (re.compile(r"-----BEGIN\s+(?:RSA|EC|OPENSSH|PGP|DSA)?\s*PRIVATE KEY-----"), "مفتاح خاصّ PEM"),
    (re.compile(r"(?:api[_\- ]?key|secret[_\- ]?key|access[_\- ]?token|auth[_\- ]?token|"
                r"client[_\- ]?secret|password|passwd|كلمة\s+(?:ال)?مرور|رمز\s+الوصول)"
                r"\s*[:=]\s*\S{6,}", re.I), "بيان اعتماد مقترن بقيمة"),
    (re.compile(r"\bBearer\s+[A-Za-z0-9_\-\.]{16,}\b", re.I), "رمز Bearer"),
]

# سطر يبدأ بـ <!-- allow-finance --> يسمح بتجاوز موضعيّ موثَّق.
ALLOW_TOKEN = "allow-boundary"


def scan_file(path: Path):
    violations = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, OSError):
        return violations  # تخطَّ غير النصّيّ
    for i, line in enumerate(lines, 1):
        if ALLOW_TOKEN in line:
            continue
        for pat, label in FINANCE_PATTERNS + SECRET_PATTERNS + CREDENTIAL_PATTERNS:
            if pat.search(line):
                violations.append((i, label, line.strip()[:120]))
                break
    return violations


def main():
    if not SCAN_DIR.exists():
        print(f"⚠️  لا يوجد مسار للفحص: {SCAN_DIR}")
        return 0
    total = 0
    for path in sorted(SCAN_DIR.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
            continue
        for ln, label, snippet in scan_file(path):
            total += 1
            rel = path.relative_to(ROOT)
            print(f"❌ {rel}:{ln} — {label}\n     {snippet}")
    if total:
        print(f"\n🚫 {total} مخالفة حدود. هذا المستودع عامّ — راجع GOVERNANCE.md.")
        print("   الأرقام الماليّة والمواد السرّيّة تُدار في قنوات المنظمة الخاصّة، لا هنا.")
        print("   لتجاوز موثَّق ضع التعليق allow-boundary على السطر.")
        return 1
    print("✅ لا مخالفات حدود.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
