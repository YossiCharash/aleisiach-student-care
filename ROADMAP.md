# ROADMAP — מערכת ניהול תלמידים (עלי שיח)

מעקב התקדמות. `[x]` = בוצע · `[ ]` = טרם · `[~]` = חלקי.
עודכן: 2026-08-27. מקורות: `CLAUDE.md`, `ARCHITECTURE.md`, `DECISIONS.md`.

> **סטטוס-על:** ה-backend הושלם כמעט במלואו — כל 4 הטאבים, אימות+הרשאות, טקסונומיה,
> audit-log, ייצוא PDF, ונעילת login. הפתוח שנותר דורש קלט/החלטה (שמות כותרות טאב 4,
> ספק מייל/גופן) או הוא ה-frontend, שטרם התחיל.

---

## 0. תכנון והחלטות
- [x] חזון, סטאק נעול, כללי עבודה (`CLAUDE.md`)
- [x] ארכיטקטורה + מודל נתונים + זרימות (`ARCHITECTURE.md`)
- [x] יומן ADR — 16 החלטות (`DECISIONS.md`)
- [x] מיתוג: צבעים חולצו מ-aleisiach.org (`#CC3366`, `#85C441`)
- [x] ADR: ניהול הרשאות — **custom** (StudentAccessPolicy/Guard), ללא Casbin
- [ ] בחירת פונט עברי סופי (Tubic מסחרי מול Heebo חינם) — נדחה לסוף
- [ ] אישור שמות כותרות 5+ בטאב 4
- [ ] בחירת ספק שליחת מיילים
- [ ] מספר תקופת שמירה (retention) לתלמיד מאורכב
- [ ] בחירת גרסת עיצוב לכניסה / מסך תלמיד

## 1. תשתית ו-DevOps
- [x] ריפו פרטי ב-GitHub + Git hooks (pre-commit/pre-push)
- [x] CI (GitHub Actions): ruff + black + mypy(strict) + pytest
- [x] מבנה שכבות מחייב (routes/service/client/schema/models/configuration/errors/utils)
- [x] Bootstrap composition-root (סינגלטונים נוצרים פעם אחת)
- [x] נתיב יבוא `backend.app`
- [ ] `.gitattributes` לנרמול שורות (LF) — מבטל אזהרות CRLF
- [ ] אירוח: frontend (סטטי/CDN), backend (קונטיינר עם ספריות WeasyPrint), PostgreSQL מנוהל
- [ ] ניהול סודות אמיתי (.env → סוד בסביבה)

## 2. Backend — אימות והרשאות
- [x] Hashing סיסמאות (argon2) + טוקנים מאובטחים (hash-only, חד-פעמי, תפוגה)
- [x] הזמנה: יצירה (מנהל) + קבלה (username+password)
- [x] כניסה (username+password) + הנפקת session token
- [x] Logout (ביטול session)
- [x] שכחתי סיסמה: בקשה נייטרלית + reset
- [x] Session + current-user + guard לפי תפקיד (`require_manager` / `ContentWriter` / policy)
- [x] Endpoint ליצירת הזמנה מוגן למנהל
- [x] **Rate-limiting + lockout** על login (נעילת חשבון) + throttle על forgot-password (per-account)
- [x] אכיפת RBAC מלאה על כל ה-routes (students · טקסונומיה · טאבים 2–4)
- [ ] הקשחת rate-limit ברמת HTTP/IP (מעבר ל-per-account) — הקשחה עתידית
- [ ] אינטגרציית ספק מייל אמיתי (כרגע ConsoleEmailSender)
- [ ] אזור משתמשים: רשימת/השבתת/הסרת משתמשים (מעבר ל-invite)

## 3. Backend — דומיינים
- [x] Students: יצירה / רשימה / שליפה / ארכוב (soft-delete) + טסטים
- [x] **סינון הרשאות על students**: מדריך→כיתתו · מורה מקצועי→read-only · `archived_by` למשתמש הנוכחי
- [x] ניהול כיתות (Class) — כרגע רק מודל
- [x] Taxonomy: Label→SubLabel→Skill→Solution + CRUD בהגדרות + `is_active` (soft-delete)
- [x] Tab 2 — ישיבות צוות: meeting + entries + בחירת צבע + פתרונות + snapshot + שמירה אטומית
- [x] Tab 1 — תוכנית (נגזר: דירוג אחרון לכל כישור חוצה כל הישיבות)
- [x] Tab 3 — הערת עו"ס (מנהל כותב, מדריך קורא, מורה מקצועי חסום)
- [x] Tab 4 — פרטי תלמיד: זהות · אבחנות · אנשי קשר · אפוטרופסות+מעמד (RBAC דו-אזורי, גיל מחושב)
- [ ] Tab 4 — כותרות נוספות (`extra_section_type` + `student_extra_section`) — חסום על שמות הכותרות
- [x] Audit log: טבלת `AUDIT_LOG` + רישום על כל create/update/archive (student · details · meeting · taxonomy · permission)
- [x] ייצוא PDF (WeasyPrint) — סיכום ישיבה + פרטי תלמיד (RTL עברי, מכבד הסתרה רגישה)

## 4. Frontend (Vite React SPA) — טרם התחיל
- [ ] Scaffold: Vite + React + TS + Tailwind RTL + shadcn/ui + design tokens + פונט
- [ ] API client + TanStack Query + החזקת token + רענון/logout
- [ ] מסך כניסה + "שכחתי סיסמה" + קבלת הזמנה
- [ ] מסך ראשי: שם עובד + רשימת תלמידים (לפי הרשאה)
- [ ] מסך תלמיד — טאב 1 (תוכנית)
- [ ] מסך תלמיד — טאב 2 (ישיבות צוות, אקורדיון דינמי + PDF)
- [ ] מסך תלמיד — טאב 3 (הערת עו"ס)
- [ ] מסך תלמיד — טאב 4 (פרטי תלמיד)
- [ ] עמוד הגדרות (מנהל): אזור משתמשים + טקסונומיה + כותרות טאב 4
- [ ] הגדרות אישיות: שינוי סיסמה
- [ ] בדיקות: Vitest + React Testing Library + Playwright (E2E)

## 5. איכות ונתונים
- [x] בדיקות יחידה לכל רכיב backend חדש (test-with-code) — 123 טסטים
- [ ] נתוני דמו (seed) לכל התפקידים והתלמידים
- [ ] בדיקות E2E מקצה-לקצה
- [ ] סקירת אבטחה לפני production

---

### הבא בתור (מומלץ)
1. **אזור ניהול משתמשים** (§2) — list/disable/remove, משלים את vertical ה-auth.
2. **Frontend scaffold** (§4) — הבסיס שממנו ייבנו כל המסכים; ה-backend מוכן.
3. **נתוני דמו + seed** (§5) — מאפשר הרצה מקצה-לקצה ופיתוח frontend מול נתונים.
4. חסומים על קלט: כותרות טאב 4, ספק מייל, בחירת גופן.
