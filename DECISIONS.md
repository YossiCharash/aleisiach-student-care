# DECISIONS — Architecture Decision Records

> Central log of the decisions taken for the Cloud Student Care System ("Aleisiach").
> Each record is short: **Context · Decision · Alternatives · Consequences**.
> Source of truth for *why*; `CLAUDE.md` and `ARCHITECTURE.md` hold the *what/how*.
> Status values: **Accepted** · **Deferred** (chosen to decide later) · **Open** (undecided).

| # | Decision | Status |
|---|---|---|
| [ADR-001](#adr-001--backend-python--fastapi--pydantic-oopsolid) | Backend = Python / FastAPI / Pydantic, OOP+SOLID | Accepted |
| [ADR-002](#adr-002--mandatory-layered-backend-structure) | Mandatory layered backend structure | Accepted |
| [ADR-003](#adr-003--frontend--vite-react-spa) | Frontend = Vite React SPA | Accepted |
| [ADR-004](#adr-004--postgresql--sqlalchemy--alembic) | PostgreSQL + SQLAlchemy + Alembic | Accepted |
| [ADR-005](#adr-005--code-standards-typing-no-comments-dtos-one-class-per-file) | Code standards (typing, no comments, DTOs, one-class-per-file) | Accepted |
| [ADR-006](#adr-006--configuration-first-minimal-hard-coding) | Configuration-first, minimal hard-coding | Accepted |
| [ADR-007](#adr-007--git-workflow-branch-per-topic-test-with-code-green-before-upload) | Git workflow (branch-per-topic, test-with-code, green gate) | Accepted |
| [ADR-008](#adr-008--exactly-three-roles-no-separate-social-worker) | Exactly three roles; no separate social-worker role | Accepted |
| [ADR-009](#adr-009--professional-teacher--read-only-everywhere) | Professional teacher = read-only everywhere | Accepted |
| [ADR-010](#adr-010--tab-1-program-is-a-derived-read-model) | Tab 1 (Program) is a derived read-model | Accepted |
| [ADR-011](#adr-011--tab-4-extra-sections-as-normalized-tables) | Tab 4 extra sections as normalized tables | Accepted |
| [ADR-012](#adr-012--taxonomy-history--snapshot--soft-delete) | Taxonomy history = snapshot + soft-delete | Accepted |
| [ADR-013](#adr-013--student-deletion--archive-only-audit-log--changes-only) | Student deletion = archive-only; audit = changes only | Accepted |
| [ADR-014](#adr-014--authentication--username--password-with-email-invitation) | Authentication = username + password with email invitation | Accepted |
| [ADR-015](#adr-015--pdf-export--server-side-weasyprint) | PDF export = server-side WeasyPrint | Accepted |
| [ADR-016](#adr-016--branding-font--colors-from-aleisiachorg) | Branding: font + colors from aleisiach.org | Accepted |

---

## ADR-001 — Backend = Python / FastAPI / Pydantic, OOP+SOLID
**Status:** Accepted · 2026-08-24
**Context:** Cloud app with role-based access to sensitive data; the team wants strict, testable,
object-oriented backend code.
**Decision:** Backend in Python 3.12+, **FastAPI**, **Pydantic v2** at every boundary (no loose
dicts), fully OOP following SOLID and design patterns (Repository, Service, Dependency Injection,
Strategy). uv for env/deps.
**Alternatives:** Node/NestJS; Supabase BaaS. Rejected in favor of Python per the team's standard.
**Consequences:** FastAPI's native DI + Pydantic map cleanly to the layered structure (ADR-002);
async-ready; OpenAPI generated for free.

## ADR-002 — Mandatory layered backend structure
**Status:** Accepted · 2026-08-24
**Context:** Need one predictable place for every concern and a strict dependency direction.
**Decision:** Top-level layers: `routes · service · client · schema · models · configuration ·
errors · utils`. The primary layers (`routes/service/client`) hold executable code; each of the
remaining layers (`schema/models/errors/utils`) is split **internally by consuming layer**
(`routes/service/client`). `configuration/` is split by area instead. Dependencies flow one way:
`routes → service → client → models`.
**Alternatives:** Domain-first foldering (per feature). Rejected — team chose layer-first.
**Consequences:** Very consistent; a feature is traced straight down the layers. New code must
copy this shape (a reference vertical slice is recommended).

## ADR-003 — Frontend = Vite React SPA
**Status:** Accepted · 2026-08-24
**Context:** The backend is a separate FastAPI service; the app is an internal, desktop-only,
authenticated tool with no SEO/public-page needs.
**Decision:** **Vite + React 18 + TypeScript** as a pure SPA talking to the API over HTTP.
Tailwind (RTL), shadcn/ui, TanStack Query, React Hook Form + Zod, react-router. pnpm.
**Alternatives:** Next.js (App Router). Rejected — SSR/Node server adds a second runtime with no
benefit for an authenticated internal tool.
**Consequences:** Simpler build and static hosting; all data access goes through the API client.

## ADR-004 — PostgreSQL + SQLAlchemy + Alembic
**Status:** Accepted · 2026-08-24
**Context:** Relational data (users, classes, students, meetings, taxonomy) with strong integrity
needs and an audit trail.
**Decision:** **PostgreSQL** with typed class-based **SQLAlchemy 2.0** models and **Alembic**
migrations. Scans/documents live in S3-compatible object storage, not the DB.
**Consequences:** Migrations are versioned and reviewable; destructive migrations require approval
(see ADR-007 / product rule 10).

## ADR-005 — Code standards (typing, no comments, DTOs, one-class-per-file)
**Status:** Accepted · 2026-08-24
**Context:** Readability and consistency are top priorities for the team.
**Decision:** (a) Clean readable code; **no comments except where unavoidable** — no narrating
comments, no commented-out code. (b) **Full typing** — every argument, variable, and an explicit
return type on every function; mypy must pass. (c) **DTO rule** — any group of 3+ values used
together more than once becomes a dedicated Pydantic DTO in `schema/`. (d) **One class per file /
one model per file.**
**Consequences:** Enforced by Ruff + Black + mypy in CI (ADR-007).

## ADR-006 — Configuration-first, minimal hard-coding
**Status:** Accepted · 2026-08-24
**Context:** Values vary by environment/deployment/business decision.
**Decision:** Every configurable setting lives under `configuration/`, organized in folders by
area (database/auth/pdf/app/email/…), via pydantic-settings. Hard-code only true constants that
should never change.
**Consequences:** Environment portability; secrets/URLs/limits are never inlined in logic.

## ADR-007 — Git workflow (branch-per-topic, test-with-code, green-before-upload)
**Status:** Accepted · 2026-08-24
**Context:** Solo/small-team development that must stay releasable.
**Decision:** (a) Every session starts on a new branch named for its topic — `feature/<topic>` or
`bug/<topic>`/`fix/<topic>`; never commit to `main`. (b) Every new component ships with its unit
test, created together (pytest, also runs `unittest.TestCase`). (c) GitHub Actions CI runs lint +
mypy + the full suite (backend and frontend) on every push/PR; a red suite blocks upload/merge.
**Update (2026-08-27):** local pre-commit/pre-push git hooks were removed — CI is the single
enforcement point for all checks.
**Consequences:** Main stays green; tests mirror the layer/domain structure under `tests/`.

## ADR-008 — Exactly three roles; no separate social-worker role
**Status:** Accepted · 2026-08-24
**Context:** The brief calls the Tab 3 note "a few words from the system manager, who is the
social worker." The user confirmed only three permission types.
**Decision:** Roles are exactly `manager`, `instructor`, `professional_teacher`. There is **no**
social-worker role — the Tab 3 note is written by **managers** (manager = social worker; all
managers may write it).
**Alternatives:** A 4th social-worker role; a manager sub-permission flag. Rejected — the manager
already fills that function.
**Consequences:** Simpler authorization; Tab 3 write is a manager capability.

## ADR-009 — Professional teacher = read-only everywhere
**Status:** Accepted · 2026-08-24
**Context:** The professional teacher sees all students but only "part" of the data; "part" needed
a precise definition.
**Decision:** Professional teacher is **read-only everywhere**: reads the student list, Tabs 1 & 2,
and the non-sensitive part of Tab 4 (identity, diagnoses, communication/preferences). **Blocked**
from Tab 3 (social-worker note) and from Tab 4's guardianship/legal-status section. No write
anywhere; no Settings.
**Consequences:** Enforced server-side in the service layer via a per-role authorization policy.

## ADR-010 — Tab 1 (Program) is a derived read-model
**Status:** Accepted · 2026-08-24 · **revised 2026-08-26** (per-skill latest, confirmed with the user)
**Context:** Saving a team meeting must "automatically update" Tab 1; storing Tab 1 separately
risks drift between it and the meetings. The original wording ("the student's latest team meeting")
was ambiguous about skills that the newest meeting did not re-assess.
**Decision:** Tab 1 is **not stored** — it is the **latest rating per skill across all** the
student's team meetings: for each skill ever assessed, the most recent meeting that rated it
decides its bucket — green → strengths (מוקדי כח); yellow/red → areas to strengthen (מוקדים
לחיזוק) with that entry's chosen solutions as the "path to solution". Each item also carries the
year/month it was last assessed. No manual editing.
**Alternatives:** **Single-latest-meeting only** — rejected, it would drop skills the newest
meeting happens not to cover, losing the accumulated picture. An editable stored snapshot —
rejected, risks drift.
**Consequences:** No `PROGRAM` table; Tab 1 is a query that walks the student's meetings
newest-first and keeps the first rating seen per skill (a final `id` tiebreaker keeps same-month
ties deterministic).

## ADR-011 — Tab 4 extra sections as normalized tables
**Status:** Accepted · 2026-08-24
**Context:** Tab 4 has additional headings (5+) beyond the fixed fields; their exact names come
from a document and may change.
**Decision:** Store them in **normalized tables**: `extra_section_type` (heading text, order,
managed in Settings) + `student_extra_section` (student_id, section_type_id, content). Heading
names are therefore **data**, editable without a schema change.
**Alternatives:** JSONB blob; fixed columns. Rejected — the user chose tables; also unblocks the
pending heading names. (`contacts`/`medical_diagnoses` stay JSONB for now.)
**Consequences:** Headings are configurable; exact wording still to be supplied but enters as rows.

## ADR-012 — Taxonomy history = snapshot + soft-delete
**Status:** Accepted · 2026-08-24
**Context:** Managers edit/delete taxonomy (labels/skills/solutions) in Settings, but past meetings
reference them; historical summaries must not break or silently change — this is a care record.
**Decision:** On meeting save, each entry copies the skill and chosen-solution **text** into
`*_snapshot` columns. Taxonomy rows are **never hard-deleted** — Settings sets `is_active=false`
(deactivated rows leave the Tab 2 form but keep FKs valid).
**Alternatives:** Soft-delete only (no snapshot) — rejected, renames would rewrite history. Full
versioning — rejected as over-complex.
**Consequences:** Historical meetings stay faithful; a small amount of denormalized text is stored.

## ADR-013 — Student deletion = archive-only; audit log = changes only
**Status:** Accepted · 2026-08-24
**Context:** Data concerns minors' medical/guardianship details; irreversible loss is unacceptable
and changes must be traceable.
**Decision:** Students are **never hard-deleted** from the app — a manager sets `is_archived`
(soft-delete), hiding them from lists while keeping data. **Audit log** records every
create/update/archive of student/details/meeting/taxonomy/permission (actor + what changed + when).
Reads are not logged; raw sensitive values are never written to the log. Retention is a
configurable period (number TBD).
**Alternatives:** Hard delete for managers; logging reads too. Rejected — too risky / too noisy.
**Consequences:** `AUDIT_LOG` table; hard deletion only via DB admin.

## ADR-014 — Authentication = username + password with email invitation
**Status:** Accepted · 2026-08-24
**Context:** The original design used username + national ID (password only for managers). A
national ID is a weak, leakable factor for sensitive minors' data.
**Decision:** **Username + password for all users.** National ID is dropped from auth (stays a
Tab 4 student field). Managers provision users in Settings → **Users area** (per user: full name,
email, role, class; bulk-invite by email). An **email invitation link** lets the user set a
username + password. Self-service password change; **forgot-password** by email with a neutral
message (no enumeration). Passwords hashed (argon2/bcrypt); invite/reset tokens are single-use,
time-expiring, and stored hashed; rate-limit + lockout on login and reset.
**Alternatives:** Keep national ID (+hardening); passwords for managers only. Rejected — weak
factor and worse UX/security.
**Consequences:** Adds `USER.email/status` and an `AUTH_TOKEN` table. The design's "conditional
manager password" login is obsolete. **Email provider (decided 2026-08-27): Gmail SMTP** —
`SmtpEmailSender` (stdlib `smtplib`, STARTTLS) selected via `EMAIL_PROVIDER=smtp` with
`EMAIL_SMTP_USERNAME`/`EMAIL_SMTP_PASSWORD` (a Gmail app password); dev defaults to the console
sender. Rate-limit + lockout on login and reset are implemented (per-account).

## ADR-015 — PDF export = server-side WeasyPrint
**Status:** Accepted · 2026-08-24
**Context:** Team-meeting summaries and student details must print/export as consistent, RTL-correct
Hebrew PDFs.
**Decision:** Generate PDFs **server-side in Python with WeasyPrint** (HTML/CSS → PDF), with an
embedded Hebrew font (see ADR-016).
**Alternatives:** Client-side `react-to-print`/browser print — rejected for inconsistent output;
ReportLab — heavier for HTML-style layouts.
**Consequences:** One rendering path; RTL/font issues solved once on the server.

## ADR-016 — Branding: font + colors from aleisiach.org
**Status:** Accepted · 2026-08-24 · **font decided 2026-08-27**
**Context:** Rule 5 requires matching Aleisiach branding, not generic defaults. Live inspection of
aleisiach.org found font **Tubic** (commercial, Fontef) and it also loads **Heebo** (OFL).
**Decision:** **Colors** as theme tokens — primary raspberry/magenta `#CC3366`, secondary green
`#85C441`, neutrals black/white + grays `#333333`/`#5C5C5C`. **Font = default (Heebo, OFL)** — the
free, embeddable Hebrew sans, used as the CSS default (`'Heebo', sans-serif`) in the PDF documents
and to be the UI default; licensing **Tubic** for an exact match stays a later, localized swap.
**Consequences:** No font licensing needed now; Heebo embeds in WeasyPrint and is installed in the
backend container for PDF rendering.

---

## Open / deferred items (not yet ADRs)
- **Tab 4 extra sections** — the manager builds the headings/sub-headings themselves in Settings
  (ADR-011 mechanism implemented); no fixed names needed.
- **Login/student-screen design variation** — pick among the design's variations (frontend).

_Resolved: Hebrew font = **Heebo** default (ADR-016); email provider = **Gmail SMTP** (ADR-014)._
