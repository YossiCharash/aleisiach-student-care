# CLAUDE.md — Cloud Student Care System ("Aleisiach")

> This file is the project's source of truth for Claude Code and for every developer.
> It holds: the project vision, the technology stack, and every rule that must be kept
> throughout development.
> **The stack in §2 is LOCKED** (confirmed with the user). Changing it requires an explicit
> decision recorded here.

Design source: Claude Design — file `Student Care System.dc.html`.




## 1. Technology Stack — **LOCKED**

> Confirmed with the user. Tuned for: a cloud app, Hebrew RTL, role-based access, sensitive data,
> and PDF export. Two separate apps: a **Vite React SPA** frontend and a **FastAPI** backend.

### Frontend — **Vite React SPA**
- **Build/framework:** **Vite** + **React 18** + **TypeScript** (pure single-page app; no SSR,
  no Node server — talks to the FastAPI backend over HTTP).
- **Styling:** Tailwind CSS + RTL support (`dir="rtl"`, logical properties / `tailwindcss-rtl`).
- **Component library:** shadcn/ui / Radix.
- **State / data fetching:** TanStack Query (React Query).
- **Forms:** React Hook Form + Zod (validation).
- **Typography:** aleisiach.org uses **Tubic** (commercial Hebrew font, Fontef). Free fallback
  **Heebo** (OFL, already loaded by the site, similar geometric Hebrew sans). Final choice for
  UI + PDF embedding is deferred (see §6).
- **Brand colors (from aleisiach.org):** primary raspberry/magenta `#CC3366`, secondary green
  `#85C441`, neutrals black/white + grays `#333333` / `#5C5C5C`. Use these as the Tailwind theme
  tokens — not generic defaults.

### Backend / Data — **Python (FastAPI)**
- **Language:** Python 3.12+ , fully **OOP**, following **SOLID** and appropriate **design patterns**
  (Repository, Service, Dependency Injection, Strategy where it fits).
- **Framework:** **FastAPI** — async, Pydantic-native, first-class DI, maps cleanly to the layered
  structure below.
- **Validation / models:** **Pydantic v2** for all schemas and DTOs; **pydantic-settings** for
  configuration. Everything that crosses a boundary is a typed Pydantic model — no loose dicts.
- **ORM:** SQLAlchemy 2.0 (typed, class-based models).
- **Migrations:** Alembic.
- **Database:** PostgreSQL.
- **Files (scans/documents):** object storage (S3-compatible) — not in the DB.
- **Layering (mandatory):** top level = `routes · service · client · schema · models ·
  configuration · errors · utils`. Each of the **latter** layers (`schema`, `models`,
  `configuration`, `errors`, `utils`) is split internally by the consuming layer —
  `routes / service / client`. See `ARCHITECTURE.md` §2.

### Additional capabilities
- **PDF export / print:** **server-side in Python (WeasyPrint)** for the team-meeting summary
  (Tab 2) and student details — consistent, RTL-correct Hebrew output. (Hebrew font choice: §6.)
- **Auth:** see section 3 — **username + password** for all users, manager-provisioned via email
  invitation, with password change and forgot-password reset. Requires an email-sending service.

### Tooling
- **Frontend package manager:** **pnpm**.
- **Python deps/env:** **uv**.
- **Lint / format:** Frontend — ESLint + Prettier · Backend — Ruff + Black + mypy (type checking).
- **Testing:** Backend — **unit tests for every new component** (pytest runner, which also runs
  `unittest.TestCase` classes); Frontend — Vitest + React Testing Library; Playwright for E2E.
- **CI/CD:** **GitHub Actions** — **every push runs the test suite; a red suite blocks merge.**
- **Git hooks:** pre-commit/pre-push runs lint + tests locally before every upload.
- **Hosting:** frontend — static host (Vercel/Netlify/any static/CDN); backend — **containerized
  FastAPI** (Railway / Fly.io / any container host); PostgreSQL — managed instance.

---

## 3. Auth & Roles Model — **password-based (decided)**

The original username + national-ID flow is **dropped**. **National ID (ת"ז) is not an auth
factor** — it remains only as a Tab 4 student data field. Login is **username + password** for all
users.

**Provisioning (manager only):** Settings → **Users area** — the manager adds/removes users. When
adding, the manager provides, per user, **full name · email · role · class** (class only for
instructors) and can add several at once (a list). Each added user is emailed an **invitation
link**.

**Invitation acceptance:** the link opens a page where the user sets a **username + password
(+ confirm)** — this becomes their login credential and activates the account.

**Login:** username + password.

**Change password:** self-service, in the user's personal settings.

**Forgot password:** on the login page → enter email → **if it exists**, a password-reset email is
sent. The UI shows the **same neutral message either way** (no email-enumeration leak).

**Security requirements (mandatory):**
- Passwords hashed with **bcrypt/argon2** — never stored or logged in plaintext.
- Invitation and reset links use **single-use, time-expiring tokens** (store only a token hash).
- **Rate-limiting + lockout** on login and on forgot-password.
- Reasonable session length/expiry; log out invalidates the session.

### Permission matrix
**Exactly three roles** (decided): `manager`, `instructor`, `professional_teacher`. There is
**no separate social-worker role** — the social-worker note (Tab 3) is written by managers (the
manager *is* the social worker; every manager may write it).

| Capability | Manager | Instructor | Professional teacher |
|---|---|---|---|
| Student list | All | Own class only | All |
| Tab 1 — Program | Read/Write | Read | Read |
| Tab 2 — Team meetings | Read/Write | Read/Write | Read |
| Tab 3 — Social-worker note | Read/Write | Read only | **Blocked** |
| Tab 4 — identity · diagnoses · communication/preferences | All | Own class | Read |
| Tab 4 — guardianship & legal status (sensitive) | All | Own class | **Blocked** |
| Settings page (taxonomy, passwords) | ✔ | ✘ | ✘ |

> **Professional teacher = read-only everywhere** (decided): sees all students, reads Tabs 1, 2
> and the non-sensitive part of Tab 4; blocked from Tab 3 and from the guardianship/legal-status
> section of Tab 4; no write anywhere; no Settings.

---

## 4. Working Rules — binding for Claude Code

1. **Do not add or change any feature/field/screen without asking first.** If something is
   undefined — stop and ask. This is the most important rule, straight from the brief.
2. **Do not invent missing information.** When a data source, field structure, or permission
   rule is missing — ask, don't assume.
3. **Hebrew and RTL everywhere.** All UI, error messages, and content in clear, correct Hebrew.
4. **Desktop only** — don't invest in mobile responsiveness unless asked.
5. **Match Aleisiach branding** — colors/font per aleisiach.org, not generic defaults.
6. **Dynamic taxonomy** — never hard-code labels/skills/solutions. They come from the DB and
   are managed on the Settings page.
7. **Sensitive-data security** — never log national IDs/diagnoses/guardianship details; never
   expose data beyond the user's permission; enforce permissions server-side too (not only in UI).
   **Deletion is archive-only** (soft-delete, manager only) — no hard delete from the app. **Audit
   log records every change** (create/update/archive of student/details/meeting/taxonomy/
   permission) — actor + what changed + when; reads are not logged, and raw sensitive values are
   never written to the log.
8. **Demo data only** during the prototype phase; do not enter real student data.
9. **Consistent terminology** — the end-user term is **"student" (תלמיד)** (not ward/patient).
10. **Ask before irreversible actions** (deletion, destructive migrations, permission changes).

### Engineering & workflow rules (backend)
11. **OOP + SOLID + design patterns.** Backend is written in classes, single-responsibility,
    dependency-inverted (inject dependencies, don't `new` them inside services). Prefer known
    patterns (Repository, Service, Factory, Strategy) over ad-hoc code.
12. **Pydantic at every boundary.** Requests, responses, config, and inter-layer DTOs are typed
    Pydantic models — never raw dicts.
13. **Layered structure is mandatory.** Code lives in `routes / service / client / schema /
    models / configuration / errors / utils`, each further split by domain. A layer only depends
    downward (routes → service → client/models); no upward or sideways imports.
14. **Branch per session/topic.** Each work session starts on a **new branch** named by its
    topic: `feature/<topic>` for new work, `bug/<topic>` (or `fix/<topic>`) for fixes. Never
    commit directly to the main branch.
15. **Every new component ships with a unit test**, created together with the code. No new
    service/route/util without its test.
16. **Tests must pass on every upload.** Before each commit/push the full suite runs (git hook +
    CI); a failing suite blocks the upload/merge.
17. **Clean, readable code is a top priority.** Express intent through clear names and small
    functions — **no comments except where there is no other choice** (e.g. a non-obvious
    workaround). No commented-out code, no narrating comments.
18. **Full typing, always.** Every function argument is typed, every variable has a defined type,
    and **every function declares an explicit return type**. `mypy` must pass.
19. **DTO for repeated value groups.** Any group of **3+ values used together more than once**
    becomes a dedicated **Pydantic DTO** (in `schema/`), not passed around as loose args/dicts.
20. **One class / one model per file.** Each class lives in its own file; each model type has its
    own separate file.
21. **Configuration-first, minimal hard-coding.** Every configurable setting lives under
    `configuration/`, organized into folders by area. Avoid hard-coded values in the code —
    the only exception is a value that should **never** change (a true constant). Anything that
    could vary by environment, deployment, or business decision is configuration.

---

## 5. Screen Map (for tracking)

- **Login screen** — username + password + a "forgot password" link. (2–3 design variations.)
- **Invitation-acceptance screen** — reached from the email link; set username + password (+ confirm).
- **Forgot-password screen** — enter email; neutral confirmation message either way.
- **Main screen** — top-right: worker name + list of students assigned to their class; clicking
  a student → student screen.
- **Student screen (tabs):**
  - Tab 1 — **Program**: strength areas + areas to strengthen (including the path to a solution).
    **Derived automatically** from the latest team meeting (not stored, not manually edited):
    green → strengths; yellow/red → areas to strengthen, with the chosen solutions as the path.
  - Tab 2 — **Team meetings**: organized by months, an "Add monthly meeting" button → a long
    accordion form (label → sub-label → skill → choose red/yellow/green = dependent/supervised/
    independent; on red/yellow a "solutions" field opens, sourced from Settings). Save = summary
    + automatic update of Tab 1 + print / PDF export.
  - Tab 3 — **Social worker note**: written by managers (manager = social worker), read-only for
    instructors, blocked for professional teachers.
  - Tab 4 — **Student details**: basic identity · emergency contacts & guardianship · official
    medical/functional diagnoses · + additional headings (5+) stored in **normalized tables**
    (`extra_section_type` + `student_extra_section`); the heading text is configurable in Settings.
    Exact heading names to be supplied by the user (draft reading was 5. preferred communication
    channel · 6. prior educational/occupational background · 7. preferences & sensitivities).
- **Settings page** (manager): **Users area** (add/remove users; per user: full name · email ·
  role · class; bulk-invite by email) + manage the taxonomy (labels / sub-labels / skills /
  solutions) + manage Tab 4 section headings.
- **Personal settings** (every user): change own password.

---

## 6. Open / needs user approval
- [ ] Supply the exact names of headings 5+ in Tab 4 (structure decided = normalized tables;
      names live as configurable rows, to be provided).
- [ ] Choose the login-screen design variation (and maybe one for the student screen too).
- [ ] Hebrew font choice for UI + PDF — **deferred to the end** (candidates: license **Tubic**
      for exact brand match, or free **Heebo**). Brand colors already captured in §1.
- [x] Auth flow — **username + password for all users** (national ID dropped from auth);
      manager-provisioned via email invitation; role + class set in the invite form; password
      change + forgot-password reset; hashed passwords, single-use expiring tokens, rate-limit +
      lockout (decided). Needs an email-sending service (provider TBD).
- [x] Define access for the professional teacher — **read-only everywhere; Tab 3 & guardianship
      blocked** (decided).
- [x] Social-worker status — **no separate role; all managers write Tab 3** (manager = social
      worker) (decided). Roles are exactly three.
- [x] Tab 1 update rule — **derived automatically from the latest meeting** (not stored/edited)
      (decided).
- [x] Deletion & audit — **archive-only (manager); audit log records changes only** (decided).
      Retention period is a config value, number TBD.
- [x] Stack — **LOCKED** (Vite React SPA + FastAPI/Pydantic + PostgreSQL; pnpm, uv, GitHub
      Actions; server-side WeasyPrint PDF) (decided).

---

_See `ARCHITECTURE.md` for the detailed technical structure, data model, and the team-meeting
form flow. See `DECISIONS.md` for the ADR log — the rationale behind every decision above._
