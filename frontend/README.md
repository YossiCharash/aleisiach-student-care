# Frontend — מערכת ניהול תלמידים (עלי שיח)

Vite + React 18 + TypeScript SPA. עברית RTL, מיתוג עלי שיח, מדבר מול ה-backend של FastAPI.

## הרצה מקומית

```bash
pnpm install
pnpm dev
```

ברירת מחדל: הפרונט עולה על `http://localhost:5173` ומפנה בקשות `/api/*` ל-`http://localhost:8000`
(ה-backend) דרך proxy מוגדר ב-`vite.config.ts`. אפשר לשנות עם `VITE_API_BASE_URL` (ראו `.env.example`).

## פקודות

| פקודה | תיאור |
|---|---|
| `pnpm dev` | שרת פיתוח |
| `pnpm build` | typecheck (`tsc --noEmit`) + build ל-production |
| `pnpm typecheck` | בדיקת טיפוסים בלבד |
| `pnpm test` | Vitest (יחידה + React Testing Library) |
| `pnpm lint` | ESLint |
| `pnpm format` | Prettier |

## מבנה

```
src/
  lib/            # api client, endpoints, types, auth (context/token/permissions), utils
  components/     # ui/ (Radix/shadcn primitives), layout/, רכיבים משותפים
  pages/          # מסכים: auth, students, student/<tabs>, settings
  test/           # הגדרת Vitest
```

## הרשאות
UI gating ב-`lib/auth/permissions.ts` משקף את מטריצת ההרשאות של ה-backend, אך **האכיפה האמיתית
בשרת** — ה-UI רק מסתיר. מורה מקצועי: קריאה בלבד, טאב 3 וטאב 4-רגיש חסומים (השרת מחזיר
`sensitive_visible=false`).

## פערים ידועים מול ה-backend
- **אין endpoint לרשימת כיתות** — יצירת תלמיד והזמנת מדריך משתמשות ב-`class_id` ידני (זמני).
- **אין endpoint שינוי-סיסמה מאומת** — "הגדרות אישיות" שולחת קישור איפוס לדוא"ל של המשתמש.
- כותרות נוספות בטאב 4 חסומות (ממתין לשמות הכותרות, כמו ב-backend).
