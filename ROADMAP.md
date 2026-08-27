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
- [x] ריפו פרטי ב-GitHub. **הבדיקות רצות ב-CI בלבד** — ה-git hooks המקומיים הוסרו
- [x] CI (GitHub Actions): backend — ruff + black + mypy(strict) + pytest · frontend — lint + typecheck + vitest + build + Playwright E2E
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
- [x] Students: יצירה / רשימה / שליפה / ארכוב (soft-delete) / **שחזור + רשימת מאורכבים** (מנהל בלבד) + טסטים
- [x] **סינון הרשאות על students**: מדריך→כיתתו · מורה מקצועי→read-only · `archived_by` למשתמש הנוכחי
- [x] ניהול כיתות (Class) — CRUD מלא: רשימה (כל משתמש מאומת) + יצירה/שינוי-שם (מנהל) + audit
- [x] Taxonomy: Label→SubLabel→Skill→Solution + CRUD בהגדרות + `is_active` (soft-delete) + **list-inactive לכל הרמות** (`GET /taxonomy/sub-labels|skills|solutions?...&include_inactive=`) — מאפשר הפעלה-מחדש
- [x] Tab 2 — ישיבות צוות: meeting + entries + בחירת צבע + פתרונות + snapshot + שמירה אטומית
- [x] Tab 1 — תוכנית (נגזר: דירוג אחרון לכל כישור חוצה כל הישיבות)
- [x] Tab 3 — הערת עו"ס (מנהל כותב, מדריך קורא, מורה מקצועי חסום)
- [x] Tab 4 — פרטי תלמיד: זהות · אבחנות · אנשי קשר · אפוטרופסות+מעמד (RBAC דו-אזורי, גיל מחושב)
- [ ] Tab 4 — כותרות נוספות (`extra_section_type` + `student_extra_section`) — חסום על שמות הכותרות
- [x] Audit log: טבלת `AUDIT_LOG` + רישום על כל create/update/archive (student · details · meeting · taxonomy · permission)
- [x] ייצוא PDF (WeasyPrint) — סיכום ישיבה + פרטי תלמיד (RTL עברי, מכבד הסתרה רגישה)

## 4. Frontend (Vite React SPA) — בפיתוח
- [x] Scaffold: Vite + React 18 + TS + Tailwind RTL + design tokens (מותג) + Heebo + Radix/shadcn primitives
- [x] API client + TanStack Query + החזקת token + logout (client typed מול סכמות ה-backend)
- [x] מסך כניסה + "שכחתי סיסמה" + קבלת הזמנה + איפוס סיסמה
- [x] מסך ראשי: שם עובד + רשימת תלמידים (לפי הרשאה, נאכף בשרת)
- [x] מסך תלמיד — טאב 1 (תוכנית, נגזר לקריאה בלבד)
- [x] מסך תלמיד — טאב 2 (ישיבות צוות, אקורדיון דינמי מהטקסונומיה + ייצוא PDF מאומת)
- [x] מסך תלמיד — טאב 3 (הערת עו"ס, כתיבה למנהל בלבד)
- [x] מסך תלמיד — טאב 4 (פרטי תלמיד, צפייה+עריכה, הסתרת מידע רגיש למורה מקצועי)
- [x] תצוגת "תלמידים בארכיון" (מנהל בלבד, מסלול `/students/archived` מאחורי `ManagerRoute` + קישור בהדר) — רשימה מ-`GET /students/archived` עם כפתור שחזור ל-`POST /students/{id}/restore`
- [x] עמוד הגדרות (מנהל): אזור משתמשים (הזמנה/השבתה/הפעלה) + אזור כיתות (יצירה/שינוי-שם) + ניהול טקסונומיה (הוספה + עריכת שם + השבתה + **הפעלה מחדש בכל הרמות**: תוויות · תת-תוויות · כישורים · פתרונות)
- [x] הגדרות אישיות: "שינוי סיסמה" — טופס אמיתי (סיסמה נוכחית + חדשה + אישור) מחווט ל-`POST /auth/password/change` (במקום שליחת קישור איפוס); ולידציית אורך/התאמה בצד הלקוח, והודעת השרת `invalid_current_password` מוצגת בעברית
- [x] בדיקות: Vitest + RTL — 26 טסטים + Playwright E2E (עשן: כניסה/ניתוב/שכחתי-סיסמה/404, ב-CI)
- [ ] כותרות טאב 4 בהגדרות — חסום על שמות הכותרות (כמו ב-backend)
- [x] **בורר כיתה** — `ClassPicker` נטען מ-`GET /classes`, מחליף את שדה `class_id` הידני ב-CreateStudentDialog/InviteUserDialog; `ClassIdField` הוסר. נוסף אזור "כיתות" בהגדרות (יצירה/שינוי-שם דרך `POST`/`PATCH /classes`)

## 5. איכות ונתונים
- [x] בדיקות יחידה לכל רכיב backend חדש (test-with-code) — 123 טסטים
- [x] נתוני דמו (seed) לכל התפקידים והתלמידים — `python -m backend.app.seed` (אידמפוטנטי): 3 תפקידים, 2 כיתות, 3 תלמידים, טקסונומיה מלאה, ישיבה+פרטים+הערת עו"ס
- [~] בדיקות E2E מקצה-לקצה — תשתית Playwright + טסטי עשן לזרימות הציבוריות; זרימות מאחורי כניסה דורשות backend+seed
- [ ] סקירת אבטחה לפני production

---

### הבא בתור (מומלץ)
1. ~~**Endpoint לרשימת כיתות** (Class CRUD)~~ — **בוצע** (PR #25).
2. ~~**נתוני דמו + seed**~~ — **בוצע** (PR #28): `python -m backend.app.seed`.
3. ~~**endpoint שינוי סיסמה מאומת**~~ — **בוצע**: `POST /auth/password/change`. נותר: חיווט frontend.
4. ~~**שחזור/רשימת תלמידים מאורכבים**~~ — **בוצע**: `GET /students/archived` + `POST /students/{id}/restore` (מנהל). נותר: תצוגת ארכיון ב-frontend.
5. ~~**list-inactive לתת-תוויות/כישורים/פתרונות**~~ — **בוצע**: `GET /taxonomy/{sub-labels,skills,solutions}?…&include_inactive=`. נותר: חיווט הפעלה-מחדש ב-frontend.
6. ~~**חיווט frontend**: בורר כיתה, שינוי סיסמה, תצוגת ארכיון, הפעלה-מחדש בטקסונומיה~~ — **בוצע** (שלב C, PRs #32/#33/#34 + הפעלה-מחדש).
7. **בדיקות E2E (Playwright)** מאחורי כניסה — כעת אפשריות עם ה-seed.
8. חסומים על קלט: כותרות טאב 4, ספק מייל, בחירת גופן, retention, והקשחת production.
