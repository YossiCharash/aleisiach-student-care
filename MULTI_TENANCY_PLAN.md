# תוכנית מעבר לריבוי־מוסדות (Multi-Tenancy)

> **סטטוס: הושלם.** שלבים 0–5 בוצעו בענף `feature/multi-tenancy-foundation`
> (ADR-018 ב-`DECISIONS.md`, `CLAUDE.md` §3 ו-`ARCHITECTURE.md` §4c).
> ארבע השאלות בסעיף 11 נענו — ההחלטות מתועדות ב-ADR-018.
> תאריך: 2026-09-02.

---

## 1. המטרה

המערכת משרתת כיום מוסד אחד. המטרה: מספר מוסדות באותה התקנה, כך ש:

- **מנהל מערכת עליון** (`super_admin`) — מנהל את רשימת המוסדות בלבד.
- **מנהל מוסד** (`manager` של מוסד) — רואה **רק** את המוסד שלו: תלמידים, כיתות,
  מדריכים, מורים מקצועיים, פגישות, טקסונומיה, הגדרות ויומן שינויים.
- **כל ישות במערכת** שייכת למוסד אחד בדיוק, ואין שום מסלול קריאה או כתיבה שחוצה מוסדות.

## 2. החלטות שהתקבלו (2026-09-02)

| # | נושא | ההחלטה |
|---|---|---|
| D1 | הרשאות מנהל־על | **ניהול מוסדות בלבד.** רואה מוסדות, יוצר מוסד, מזמין לו מנהל, משבית מוסד. **אין לו גישה לתלמידים, פגישות, הערות עו"ס או נתונים רגישים** — בשום מוסד. |
| D2 | טקסונומיה, כותרות טאב 4, קטלוג אבחונים, קטלוג אפשרויות | **פר-מוסד.** כל מוסד מנהל את שלו בעמוד ההגדרות. בהקמת מוסד חדש מועתקת **תבנית ברירת מחדל** הניתנת לעריכה. |
| D3 | שיוך משתמש | **משתמש שייך למוסד אחד בדיוק.** אין טבלת חברוּת ואין בורר מוסד. |
| D4 | זיהוי המוסד בהתחברות | **נגזר אוטומטית מהחשבון.** מסך ההתחברות **אינו משתנה** — שם משתמש + סיסמה בלבד. |

### D3+D4 — יישוב הסתירה בין ייחודיות שם המשתמש לייחודיות המייל

מכיוון שהמוסד נגזר מהחשבון (D4), **שם המשתמש חייב להישאר ייחודי בכל המערכת** —
אחרת אי אפשר לזהות מי מתחבר. לעומת זאת **המייל הופך לייחודי בתוך המוסד בלבד**,
כדי שאדם שעובד בשני מוסדות יוכל לקבל שני חשבונות עם אותה כתובת.

מכאן שתי השלכות שחייבות טיפול:

1. **קבלת הזמנה** — המשתמש בוחר שם משתמש; אם הוא תפוס במערכת (גם במוסד אחר)
   תוצג שגיאת `UsernameAlreadyUsedError` הקיימת. אין דליפת מידע: השגיאה אינה חושפת
   באיזה מוסד השם תפוס.
2. **שכחתי סיסמה** — כתובת מייל אחת עשויה להתאים לכמה חשבונות. הפתרון:
   נשלח מייל איפוס **לכל חשבון תואם**, וגוף המייל מציין את **שם המוסד ושם המשתמש**
   שאליו הקישור שייך. ההודעה במסך נשארת ניטרלית וזהה בכל מקרה (ללא דליפת קיום מייל).

## 3. מודל הנתונים

### 3.1 טבלה חדשה — `institutions`

| עמודה | טיפוס | הערות |
|---|---|---|
| `id` | UUID | PK |
| `name` | String(200) | שם המוסד, מוצג בממשק |
| `code` | String(40) | מזהה קצר ייחודי, לשימוש תפעולי ובלוגים |
| `is_active` | Boolean | ברירת מחדל `true`; השבתה = "ארכוב" (כלל 7 — אין מחיקה קשה) |
| `created_at` | DateTime(tz) | |
| `deactivated_at` | DateTime(tz) \| null | |
| `deactivated_by` | UUID \| null | מזהה מנהל־העל שביצע |

מודל: `models/client/institution.py` (מחלקה אחת לקובץ, כלל 20).

### 3.2 תפקיד חדש — `super_admin`

`UserRole` מקבל ערך רביעי: `SUPER_ADMIN = "super_admin"`.
בבסיס הנתונים `users.role` הוא `String(32)` ללא `CHECK` — **אין צורך במיגרציה**
עבור הוספת הערך עצמו.

`users.institution_id` הוא **nullable**, עם החוזה הבא הנאכף גם ב-DB:

```
CHECK ( (role =  'super_admin' AND institution_id IS NULL)
     OR (role <> 'super_admin' AND institution_id IS NOT NULL) )
```

כלומר: מנהל־על הוא המשתמש היחיד ללא מוסד, וכל משתמש אחר חייב מוסד.

### 3.3 סיווג הטבלאות הקיימות

**רמה א' — ישויות מוסד ישירות. מקבלות עמודת `institution_id NOT NULL` + FK:**

`users` (nullable, ראו 3.2) · `classes` · `students` · `labels` · `sub_labels` ·
`skills` · `solutions` · `extra_section_types` · `detail_options` ·
`diagnosis_catalog` · `audit_logs` (nullable — פעולות מנהל־על אינן שייכות למוסד).

הנימוק לכלול את כל ארבע רמות הטקסונומיה: ה-API של הטקסונומיה פונה לישויות
**לפי מזהה ישיר** (למשל `PATCH /taxonomy/skills/{skill_id}`), ולכן כל רמה חייבת
להיות ניתנת לסינון בעצמה ולא רק דרך אביה.

**רמה ב' — ילדים של תלמיד או של משתמש. ללא עמודה; השיוך נגזר מההורה:**

`student_details` · `student_extra_sections` · `social_notes` · `team_meetings` ·
`meeting_entries` · `meeting_entry_solutions` · `auth_tokens` · `user_sessions`.

הכלל המחייב: **כל גישה לרמה ב' עוברת דרך `StudentAccessGuard` (או דרך המשתמש
המאומת)** — כפי שקורה היום. תוספת: לכל מסלול ברמה ב' ייכתב טסט בידוד ייעודי (§8).

### 3.4 שינויי אילוצים

| אילוץ | היום | אחרי |
|---|---|---|
| `users.email` | `UNIQUE` גלובלי | `UNIQUE (institution_id, email)` **+** `UNIQUE (email) WHERE institution_id IS NULL` (כדי שגם מנהלי־על לא יתנגשו) |
| `users.username` | `UNIQUE` גלובלי | **ללא שינוי** — נדרש ל-D4 |
| `classes.name` | ללא | `UNIQUE (institution_id, name)` |
| `institutions.code` | — | `UNIQUE` |

**שלמות היררכית חוצת-מוסדות** — כדי שאי אפשר יהיה לקשור ילד למוסד אחר,
כל הורה ברמה א' מקבל `UNIQUE (id, institution_id)`, והילד מקבל **מפתח זר מורכב**:

```
sub_labels          (label_id,      institution_id) -> labels              (id, institution_id)
skills              (sub_label_id,  institution_id) -> sub_labels          (id, institution_id)
solutions           (skill_id,      institution_id) -> skills              (id, institution_id)
students            (class_id,      institution_id) -> classes             (id, institution_id)
users               (class_id,      institution_id) -> classes             (id, institution_id)
extra_section_types (parent_id,     institution_id) -> extra_section_types (id, institution_id)
```

זהו קו ההגנה שאינו תלוי בקוד: גם באג בשירות לא יוכל ליצור ערבוב בין מוסדות.

## 4. אכיפה בצד השרת — שלוש שכבות

### שכבה 1 — הקשר מוסד מפורש (`TenantContext`)

DTO חדש ב-`schema/service/tenant_context.py` (כללים 12 ו-19):

```python
class TenantContext(BaseModel):
    institution_id: uuid.UUID
    institution_name: str
```

נבנה פעם אחת ב-`routes/security.py` מתוך המשתמש המאומת, ומוזרק לשירותים ולמאגרים.
**לעולם לא מגיע מגוף הבקשה או מפרמטר** — זהו הכלל שמונע הסלמת הרשאות.

תלויות חדשות ב-`routes/security.py`:

- `Tenant` — מחזירה `TenantContext`; זורקת `AuthorizationError` אם למשתמש אין מוסד
  (כלומר: **מנהל־על חסום מכל מסלול מוסדי**).
- `SuperAdmin` — מאשרת `role == SUPER_ADMIN` בלבד.
- `Manager` / `ContentWriter` / `SocialNoteReader` הקיימות — נשארות, אך כולן
  יחייבו גם `Tenant`, כך ש-`super_admin` לא ייכנס דרכן בטעות.

### שכבה 2 — סינון אוטומטי בכל שאילתה (`TenantScoped`)

Mixin ב-`models/client/tenant_scoped.py` המוסיף `institution_id`, ובנוסף
מאזין ORM יחיד ב-`client/database/tenant_filter.py`:

```python
@event.listens_for(Session, "do_orm_execute")
def _apply_tenant_filter(state): ...   # with_loader_criteria על כל מחלקה יורשת TenantScoped
```

המאזין מוסיף `WHERE institution_id = :current` לכל `SELECT` על ישות רמה א',
כולל טעינות עצלות (lazy loads). זהו **מנגנון "שוכח לא מסוכן"**: מפתח שיוסיף מאגר
חדש ולא יזכור לסנן — יסונן בכל זאת. מנהל־על מריץ בהקשר מיוחד שבו הסינון כבוי,
והקשר זה נגיש רק למסלולי `/institutions`.

בכתיבה: `institution_id` נקבע במקום אחד — `TenantEntityFactory` בשכבת ה-service —
ולא בכל שירות בנפרד.

### שכבה 3 — התנהגות בגישה חוצת-מוסד

גישה לישות של מוסד אחר מחזירה **404 `NotFoundError`**, לא 403 — בעקביות עם
`StudentAccessGuard` הקיים, וכדי לא לחשוף קיום של ישות זרה.

`StudentAccessScope` יורחב: קודם סינון מוסד, ורק אחר כך סינון כיתה למדריך.

> **הקשחה עתידית (מחוץ להיקף הנוכחי):** Postgres Row-Level Security עם
> `SET LOCAL app.institution_id` לכל טרנזקציה. מומלץ כשלב מאוחר; שכבות 1–2 מספיקות
> להשקה ואינן דורשות שינוי תפעולי.

## 5. API חדש ומשתנה

### 5.1 ראוטר חדש `/institutions` — מנהל־על בלבד

| מסלול | תיאור |
|---|---|
| `GET /institutions` | רשימת מוסדות + **מונים בלבד** (מס' משתמשים, מס' תלמידים פעילים). ללא שמות תלמידים. |
| `POST /institutions` | יוצר מוסד `{name, code}` **+** מזמין את מנהל המוסד הראשון `{full_name, email}` **+** מזריע תבנית ברירת מחדל. פעולה אטומית אחת. |
| `GET /institutions/{id}` | מטא-דאטה בלבד. |
| `PATCH /institutions/{id}` | שינוי שם. |
| `POST /institutions/{id}/deactivate` | השבתה. דורשת אישור מפורש בממשק (כלל 10). |
| `POST /institutions/{id}/activate` | החזרה לפעילות. |

שכבות: `client/institutions/institution_repository.py`,
`service/institutions/institution_service.py`,
`service/institutions/institution_provisioning_service.py` (יצירה + הזמנה + הזרעה).

### 5.2 שינויים במסלולים קיימים

- `POST /auth/login` — חוזה זהה. נוספת בדיקה: מוסד מושבת → כשלון התחברות עם
  הודעה עברית ייעודית (`InstitutionInactiveError`). מנהל־על מתחבר רגיל.
- `LoginResponse.user` (`UserResponse`) — מתווספים `institution_id` ו-`institution_name`
  (עבור `super_admin`: `null`). הפרונט צריך אותם לניתוב ולכותרת.
- `POST /auth/invitations` — `InvitationCommand` מקבל `institution_id`, אך הוא
  **נקבע מהמנהל המזמין ולא מגוף הבקשה**. רק זרימת יצירת המוסד מציבה אותו במפורש.
- כל שאר המסלולים — ללא שינוי חוזה; רק סינון פנימי.

### 5.3 הזרעה ותבנית ברירת מחדל

- `configuration/institutions/default_template_settings.py` — מקור ותוכן התבנית (כלל 21).
- `seed/institution_template_seeder.py` — מעתיק טקסונומיה, כותרות טאב 4,
  קטלוג אבחונים וקטלוג אפשרויות פרטים למוסד החדש.
- `seed/bootstrap_admin_seeder.py` — **משתנה**: כיום מזריע `manager` ראשון אם אין;
  מעתה מזריע **`super_admin`** אם אין. `BootstrapAdminSettings` מתעדכן בהתאם.
- `seed/demo_seeder.py` — יוצר מוסד דמו ומשייך אליו את כל נתוני הדמו.

## 6. מיגרציה — `0016_institutions`

הנתונים כיום הם נתוני דמו בלבד (כלל 8), ולכן המהלך פשוט: **מוסד ברירת מחדל** אחד.

1. יצירת `institutions`.
2. הזרקת שורת מוסד ברירת מחדל (שם מקונפיגורציה, ברירת מחדל "מוסד ראשי").
3. הוספת `institution_id` **nullable** לכל טבלאות רמה א'.
4. `UPDATE` — מילוי כל השורות הקיימות במזהה מוסד ברירת המחדל.
5. הפיכת העמודה ל-`NOT NULL` (למעט `users` ו-`audit_logs`).
6. הסרת `UNIQUE` על `users.email` והחלפתו בזוג האילוצים מ-§3.4.
7. הוספת `UNIQUE (id, institution_id)` להורים, והמפתחות הזרים המורכבים.
8. הוספת ה-`CHECK` על `role`/`institution_id`.
9. אינדקסים: `(institution_id)` על כל טבלת רמה א'; `(institution_id, class_id)`
   על `students`; `(institution_id, created_at)` על `audit_logs`.

`downgrade` סימטרי מלא. הרצת המיגרציות כבר קורית בעליית הקונטיינר (קומיט `57242e1`).

## 7. פרונט-אנד

- `UserResponse` בטיפוסים: `institution_id`, `institution_name`, ו-`role` מורחב.
- **`ProtectedRoute`** — מקבל `allowedRoles`; `super_admin` מנותב ל-`/institutions`,
  שאר התפקידים ל-`/students`. `super_admin` שינסה `/students` יקבל הפניה, לא שגיאה.
- **עמוד חדש `InstitutionsPage`** — טבלת מוסדות, דיאלוג "מוסד חדש"
  (שם · קוד · שם ומייל מנהל המוסד), כפתור השבתה עם דיאלוג אישור.
  עיצוב עקבי עם כרטיסי הירוק הבהיר שהוכנסו בקומיט `4bb9b87`.
- **כותרת עליונה** — למשתמשי מוסד מוצג שם המוסד ליד שם המשתמש; למנהל־על מוצג
  "ניהול מוסדות".
- `SettingsPage` — ללא שינוי מבני; היא כבר פר-מוסד מרגע שה-API מסונן.
- `endpoints.ts` — `institutionsApi` חדש.

## 8. טסטים

מעבר לכלל 15 (טסט לכל רכיב חדש), נדרשים מודולי בידוד ייעודיים:

- `tests/routes/test_tenant_isolation.py` — טסט פרמטרי העובר על **כל מסלול מוסדי**:
  יוצר שני מוסדות עם נתונים, מתחבר כמשתמש של מוסד א', ומוודא **404** על כל ישות
  של מוסד ב' — כולל רמה ב' (פגישות, הערות עו"ס, פרטי תלמיד, סעיפים נוספים).
- `tests/routes/test_super_admin_boundaries.py` — מנהל־על מקבל **403** על כל מסלול
  מוסדי, ומשתמש מוסדי מקבל 403 על `/institutions`.
- `tests/service/test_tenant_filter.py` — המאזין מסנן גם בטעינה עצלה.
- `tests/service/test_institution_provisioning.py` — יצירת מוסד מזריעה תבנית ושולחת הזמנה.
- `tests/seed/test_bootstrap_admin_seeder.py` — עדכון: מזריע `super_admin`.
- 71 קבצי הטסטים הקיימים — יעודכנו לספק הקשר מוסד דרך fixture משותפת ב-`tests/support`.

## 9. שלבי ביצוע וענפי עבודה

| שלב | ענף | תוכן | תלוי ב |
|---|---|---|---|
| 0 | `feature/multi-tenancy-decisions` | ADR ב-`DECISIONS.md`, עדכון `CLAUDE.md` §3+§5 ו-`ARCHITECTURE.md` §2 | — |
| 1 | `feature/institution-model` | מודל `Institution`, `TenantScoped`, מיגרציה `0015`, `TenantContext` | 0 |
| 2 | `feature/tenant-enforcement` | מאזין הסינון, תלויות `Tenant`, עדכון כל המאגרים והשירותים, מודולי טסטי הבידוד | 1 |
| 3 | `feature/super-admin-institutions` | תפקיד `super_admin`, ראוטר `/institutions`, provisioning, תבנית ברירת מחדל, seeder | 2 |
| 4 | `feature/institutions-console-ui` | `InstitutionsPage`, ניתוב לפי תפקיד, שם מוסד בכותרת | 3 |
| 5 | `feature/multi-tenancy-hardening` | "שכחתי סיסמה" רב-חשבונות, מוסד ב-PDF ובהתראות WhatsApp, בחינת RLS | 4 |

כל שלב = PR קצר אחד עם CI ירוק לפני מיזוג (כללים 14 ו-16).

## 10. סיכונים ונקודות תשומת לב

1. **דליפה חוצת-מוסד היא כשל אבטחה חמור** בהינתן רגישות הנתונים (כלל 7).
   לכן שלוש השכבות, ולכן מודול הבידוד הוא תנאי מיזוג לשלב 2 — ולא נדחה לשלב 5.
2. **התראות WhatsApp** — יתווסף `institution_code` למטא-דאטה של ההתראה בלבד;
   לעולם לא שם מוסד/תלמיד או תוכן חופשי (כלל 25).
3. **יומן שינויים** — `audit_logs.institution_id` מאפשר למנהל מוסד לראות רק את
   היומן שלו. פעולות מנהל־על נרשמות עם `institution_id = NULL`, והמוסד המושפע
   מזוהה בשדה `entity_id`.
4. **דוחות PDF** — כותרת המסמך תכלול את שם המוסד; דורש עדכון קטן בתבניות.
5. **ביצועים** — כל שאילתה מקבלת תנאי נוסף; האינדקסים בסעיף 6.9 מכסים זאת.
   אין צפי לפגיעה בהיקפים הנוכחיים.

## 11. פתוח לאישור לפני תחילת העבודה

- [ ] שדות נוספים ל-`institutions` מעבר לשם/קוד? (איש קשר, טלפון, לוגו לדוחות)
- [ ] תוכן תבנית ברירת המחדל — להעתיק את הטקסונומיה של המוסד הקיים, או להתחיל
      מרשימה מצומצמת שתסופק?
- [ ] האם מנהל־על יכול **לאפס סיסמה** למנהל מוסד, או רק לשלוח הזמנה מחדש?
- [ ] מה קורה למשתמשים מחוברים כשמוסד מושבת — ניתוק מיידי (ביטול כל ה-sessions)
      או המתנה לפקיעת הטוקן?
