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

## ADR-017 — Continuous deployment = Render deploy hooks, gated by CI on `main`
**Status:** Accepted · 2026-09-02
**Context:** The stack (§1) fixes a containerized FastAPI backend, a static/SPA frontend and a
managed PostgreSQL, but nothing in the repo described how a merge reaches production — deploys were
configured by hand in a provider dashboard.
**Decision:** Production runs on **Render** (backend Docker service · nginx SPA service · managed
PostgreSQL), described as infrastructure-as-code in `render.yaml`. Render's own auto-deploy is
**off**; `.github/workflows/deploy.yml` triggers on a **successful CI run on `main`** and calls each
service's **Deploy Hook** with `ref` set to the exact commit CI tested, backend first and then the
frontend.
**Alternatives:** Render's push-based auto-deploy — rejected, it ships a red suite (rule 16);
the Render REST API with status polling — rejected in favour of the hook: the API would report
whether a deploy reached `live`, but its key is account-wide, while a hook URL can only deploy the
single service it belongs to; tag-triggered releases — rejected as premature for a single-environment
prototype; GHCR images plus a self-managed host — more infrastructure than this project needs.
**Consequences:** The pipeline reports that a deploy was **accepted**, not that it succeeded — a
failed build or start surfaces in Render's dashboard and notification emails, not as a red
workflow. Ordering between the two services is best-effort for the same reason. One environment
(production) for now; adding staging means a second service set and a branch/approval rule.
Migrations stay outside the pipeline — the container entrypoint runs `alembic upgrade head` on
every start. Two repository secrets (the hook URLs) are the pipeline's only credentials; setup is
documented in the README.

## ADR-018 — Multi-tenancy: many institutions, one platform super admin
**Status:** Accepted · 2026-09-02
**Context:** The system was built for a single institution. It must now serve several institutions
from one deployment, where a manager sees only their own institution and a platform operator
manages the list of institutions. The data is sensitive (minors' medical and guardianship
details), so a leak across institutions is a security failure, not a display bug.
**Decision:**
- A new `INSTITUTION` table. Every institution-owned row carries `institution_id`: classes,
  students, the four taxonomy levels, extra-section types, detail options, the diagnosis catalog,
  users and audit logs. Rows that hang off a student — details, extra sections, meetings, meeting
  entries, entry solutions and social notes — carry it too (added by `0018_tenant_scope_content`;
  they originally inherited it through their parent and relied on `StudentAccessGuard` alone).
- A fourth role, **`super_admin`** — the only account with no institution. It manages the list of
  institutions and **has no access to any institution's data**, in any institution.
- Isolation is enforced in three layers: `TenantBinding` puts the signed-in user's institution on
  the SQLAlchemy session; `TenantFilter` adds a global `WHERE institution_id = …` to every ORM
  select and stamps new rows on flush; composite foreign keys make a cross-institution parent/child
  link impossible in the database. Cross-institution access answers **404**, never 403, so a
  foreign row's existence is not disclosed.
- Taxonomy, Tab 4 headings, the diagnosis catalog and the detail-option catalog are **per
  institution**. A new institution is provisioned with the structural detail-option catalog and an
  invitation to its first manager.
- **Usernames stay unique platform-wide** so the institution is derived from the account and the
  login screen is unchanged; **e-mail is unique within an institution**, so one person can hold
  separate accounts in two institutions.
- Deactivating an institution is archive-only (rule 7): its data is kept and its users cannot log
  in, effective immediately for existing sessions.
**Alternatives:** A database per institution — rejected as operationally heavy for this scale.
A shared taxonomy owned by the super admin — rejected, it removes the flexibility of rule 6.
Per-institution usernames with an institution selector at login — rejected, it changes the login
screen for every user to serve a rare case.
**Consequences:** Migration `0016_institutions` backfills all existing rows into a default
institution. Postgres row-level security remains available as a later hardening layer on top of the
application filter.
**Follow-up decisions (2026-09-02):**
- A new institution starts with the structural detail-option catalog only; taxonomy, Tab 4 headings
  and the diagnosis catalog are built by its manager in Settings. No default content is invented.
- An institution carries a **contact name and phone** beyond its name and code; no address, no logo.
- The super admin can **re-send a pending manager invitation** and nothing more — it never resets a
  password and cannot re-invite a manager who already accepted, which would be an account takeover.
  A manager who lost access uses forgot-password.
- **Forgot-password sends one link per matching account**, each naming the institution and username;
  the on-screen message stays neutral either way.
- Unexpected-error alerts carry the **institution code** as metadata (never the name or any PII), and
  PDF exports carry the institution name in their header.

**Follow-up decision (2026-09-03) — the student-owned tables join the other two layers:**
A security review found that `team_meetings`, `meeting_entries`, `meeting_entry_solutions`,
`social_notes`, `student_details` and `student_extra_sections` carried no `institution_id`, so the
ORM filter and the composite keys did not reach them and `StudentAccessGuard` was the only thing
holding tenants apart. No leak existed — every service did call the guard — but a future query that
skipped it would have crossed institutions silently. `0018_tenant_scope_content` gives all six the
column, backfilling each row from its parent so existing institutions keep their own data, and
links them with composite keys. The guard stays the first gate and still answers 404; the other two
layers are now the backstop the ADR always claimed.

---

## ADR-019 — Tab 1 (Program) is a manually authored document, not derived from meetings

> _Superseded by [ADR-021](#adr-021--tab-1-program-splits-into-rating-only-foci--dated-versioned-plans):
> the single dateless program document is replaced by a rating-only **foci** document plus a
> **dated, versioned personal plan**. ADR-019's core point — Tab 1 is manually authored and not
> derived from meetings — still holds._

**Date:** 2026-09-08
**Decision:** The promotion program (Tab 1) is a **stored, manually authored document** — **one
program per student** — created and edited by the **manager only**, replacing the earlier
auto-derived read-model (ADR superseded: "latest rating per skill across team meetings"). It is
authored through the same accordion form as a team meeting (label → sub-label → skill →
red/yellow/green, with a solutions field on yellow/red) but **without a month/year**. The read view
splits the stored entries into strengths (green) and areas to strengthen (yellow/red), and a separate
**personal-plan** card lists the solution paths of the areas to strengthen. Instructors and
professional teachers read only. **Team meetings no longer feed the program**; they remain their own
tab (unchanged). A new **functional-report-summary** tab (Tab 5, read-only for every role) surfaces
the emotional-identity and preferred-communication cards from the Tab 4 details. _(The Tab 5 clause
is superseded by [ADR-020](#adr-020--tab-5-functional-report-is-a-manager-authored-form-30): Tab 5
is now an authored form, not a read-only surfacing of Tab 4 cards.)_

**Context:** The client reframed the student screen around a manually curated promotion plan rather
than a value computed from meeting history. The team-meeting form's rating→bucket semantics were kept
because they already match how the staff think about strengths vs. areas to strengthen.

**Data model:** new tenant-scoped tables `programs` / `program_entries` / `program_entry_solutions`
(migration `0021_manual_program`), mirroring the meeting tables minus the date, with a unique
`student_id`. The skill/solution validation and text-snapshotting is shared with the meeting service
through `SkillRatingResolver`; the identical entry-request DTO is the shared `SkillRatingRequest`.
`Program.author_id` records the **creator** and is not overwritten on edit (edits are tracked by
`updated_at` and the audit log, `entity_type="program"`).

**Alternatives:** Keep the derived read-model and add manual overrides — rejected as two sources of
truth for the same view. Allow several program versions per student — rejected; one living document
is what the client asked for. Give instructors write access (as they have on team meetings) —
rejected; the client scoped program authoring to the manager.

**Consequences:** Existing team-meeting rows no longer influence Tab 1 (in the prototype they are
demo data). There is no delete endpoint for a program, and an empty upsert is rejected
(`entries` `min_length=1`), so a program cannot be created empty. PDF export for the program is
deferred.

---

## ADR-020 — Tab 5 (Functional report) is a manager-authored form ("Form 33")

**Date:** 2026-09-08
**Decision:** The functional-report tab (Tab 5) is a **stored, manually authored document** — **one
report per student that is updated in place** — modeled on the client's official **"טופס 33 — סיכום
דוח תפקודי"**. It is **written by the manager only**; instructors and professional teachers **read
only** (unlike Tab 3, the professional teacher is *not* blocked here). The report holds six free-text
sections — **רקע כללי · התחום התעסוקתי · התחום ההתנהגותי-רגשי · התחום התקשורתי-חברתי · תחום עצמאות
וכישורי חיים · סיכום והמלצות**. The identity header (**שם · מספר ת.ז · תאריך לידה**) is **auto-filled**
from the student record and Tab 4 details — never re-keyed and never stored on the report. The form's
**"נכתב על ידי"** (the issuer) and the report date are **auto-captured** from the manager who saves and
the save time — not free-text fields. A server-side **WeasyPrint PDF** (ADR-015) exports the full
report. This **supersedes the Tab 5 clause of ADR-019** (Tab 5 was a read-only surfacing of the
emotional-identity and preferred-communication cards); those cards remain available in Tab 4.

**Context:** The client supplied the actual Form 33 and asked that Tab 5 hold everything in it and be
issuable as a filled report. The earlier read-only summary did not let anyone author the narrative
functional assessment the form is built around.

**Data model:** new tenant-scoped table `functional_reports` (migration `0022_functional_report`),
keyed by `student_id` (one per student), with the six section columns plus `updated_by` / `updated_at`;
it mirrors the `social_notes` shape (Tab 3) widened to the six sections. Identity is resolved at read
time from `Student.full_name` and `StudentDetails` (national id, date of birth); the issuer name is
resolved from `updated_by`. Audited under `entity_type="functional_report"` (create/update, field
names only — the national id value is never written to the audit log).

**Alternatives:** Keep several dated report versions per student — rejected; the client asked for one
living document (consistent with ADR-019's program). Make "נכתב על ידי" and the date free-text as in
the paper form — rejected; auto-capturing the acting manager and save time is more reliable and matches
the "filled by whoever issues it" intent. Let instructors author it (as on team meetings) — rejected;
the client scoped authoring to the manager.

**Consequences:** There is no delete endpoint; a report is created lazily on first save and identity
shows even before a report exists. The six section headings are fixed constants (they are the official
form's headings), not Settings-managed taxonomy. If the client later wants a manual issue date or a
free-text issuer, both are additive.

---

## ADR-021 — Tab 1 (Program) splits into rating-only foci + dated, versioned plans

**Date:** 2026-09-09
**Decision:** Tab 1 becomes **two sub-tabs backed by two separate stored documents**, both
**manager-write / everyone-else read-only**:

1. **Foci** (מוקדי כוח ומוקדים לחיזוק) — one current **rating-only** document per student. Authored
   through the accordion (label → sub-label → skill), but each skill is rated by **checking one of
   three rows** (top = green/עצמאי → strength, middle = yellow/בהשגחה, bottom = red/בתלות → area to
   strengthen). **No solutions are chosen here**, and the read view shows only strengths and areas —
   no solution text.
2. **Personal plan** (תוכנית אישית) — a **dated, versioned series**. Creating a plan reads the
   **latest foci's areas to strengthen** and lets the manager pick the **solution paths** (from
   Settings taxonomy) per area; it saves as a new version **stamped with its `created_at` date**.
   Each new plan leaves the previous ones untouched as **history** (a "היסטוריה" button reveals
   them). A plan snapshots **only the areas + chosen solutions** (green strengths stay in the foci
   document). Export is a **per-version PDF** plus a **combined report across all dates**
   (server-side WeasyPrint, ADR-015).

This **supersedes ADR-019's** single dateless program: solutions move out of the foci and into the
versioned plans, and the plan gains dates, history and reports. Team meetings still do **not** feed
Tab 1 (ADR-019's other point stands).

**Context:** The client asked that the foci tab only capture the strength/weakness picture (a simple
one-of-three-rows mark, not the three labelled buttons), and that the "plan" be a living record over
time — each revision kept, printable per date and as a full history — rather than a single editable
card. Choosing solutions belongs to *planning*, not to marking foci, so the two were separated.

**Data model:** `program_entry_solutions` is **dropped**; `programs` / `program_entries` stay as the
**foci** store (rating only). New tenant-scoped tables `program_plans` / `program_plan_entries` /
`program_plan_solutions` (migration `0024_program_plans`) hold the versioned plans — a plan row per
version keyed by `student_id` with `created_at`, its entries snapshotting skill name + rating, and
their chosen solutions snapshotting solution text. Foci resolve through a new rating-only
`SkillFocusResolver` (the meetings' `SkillRatingResolver`/`SkillRatingRequest` are unchanged and
still power Tab 2). Plans are audited under `entity_type="program_plan"` (create); foci stay
`entity_type="program"`. Since the prototype holds demo data only, the migration rebuilds cleanly
with no data conversion.

**Alternatives:** Keep solutions on the foci and add a date to the one document — rejected; the
client wanted history, not an editable single card. Version the foci too — rejected; only the plan
needs history, the foci are the current picture. Reuse `SkillRatingResolver` for foci — rejected; it
requires a solution on yellow/red, which foci must not carry, so a dedicated rating-only resolver is
clearer.

**Consequences:** A plan can only be built once foci with at least one area to strengthen exist
(creating one otherwise returns a 422 `invalid_plan`). Plans are create-only and immutable — there is
no plan edit or delete endpoint; a correction is a new version. A plan entry that references a skill
which is no longer a current foci area, or a solution not belonging to its skill, is rejected at save.
The combined report renders every version chronologically in one PDF.

---

## ADR-022 — Tab 2 (Team meetings) becomes a dated snapshot of foci + plan with a summary

**Date:** 2026-09-09
**Decision:** A team meeting is no longer its own skill-rating form. Opening a new meeting now
**freezes a read-only snapshot** of the student's current **foci** (מוקדי כוח ומוקדים לחיזוק) and
**latest personal plan** (תוכנית אישית) at that moment, alongside a single free-text **summary**
(סיכום). Meetings are keyed **by date** (a manager/instructor picks `meeting_date`, defaulting to
today) rather than by month. The snapshot is immutable; only the **summary stays editable** after
saving. Each meeting in the history exports to a **per-meeting PDF** (server-side WeasyPrint,
ADR-015). Write access is unchanged (manager + instructor write, professional teacher reads).

This **supersedes the Tab-2 parts of ADR-019/ADR-021** (the accordion rating form with per-skill
red/yellow/green + solutions is removed) while leaving Tab 1 itself intact — team meetings still do
not feed Tab 1; they now *read* from it.

**Context:** The client asked that a team meeting present the student's current foci and personal
plan for discussion, unchangeable in that view, with a large summary field — and that the record
keep the foci and plan **as they were at the time of the meeting**, dated, printable per meeting.
The meeting is therefore a point-in-time minutes document, not an editing surface.

**Data model:** the old `team_meetings` (year/month) / `meeting_entries` / `meeting_entry_solutions`
tables are **dropped**. `team_meetings` is rebuilt with `meeting_date` (Date), `summary` (Text),
`author_id`, `created_at`, `updated_at`. Three tenant-scoped snapshot tables hold the frozen copy
(migration `0025_meeting_snapshots`): `meeting_foci_entries` (skill name + rating), and
`meeting_plan_entries` / `meeting_plan_solutions` (skill name + rating + chosen solution text).
`MeetingService.create` copies the current `Program` and the latest `ProgramPlan` into these tables;
a meeting created with no foci/plan yet is allowed (empty snapshot + summary). `update_summary`
(HTTP `PATCH`) changes only the summary. Meetings are audited under `entity_type="team_meeting"`
(create + summary update). Since the prototype holds demo data only, the migration rebuilds cleanly
with no data conversion.

**Alternatives:** Store the snapshot as a single JSON column on the meeting — rejected; normalized
tables match the `program_plan` precedent, keep `TenantScoped` + composite foreign keys enforcing
institution isolation, and honour the "no loose dicts" rule. Reference the live `Program`/plan by id
instead of copying — rejected; foci are mutable (upsert overwrites), so only a copy freezes the
picture. Lock the summary after save — rejected; the client asked to keep editing the summary.

**Consequences:** A meeting's foci/plan view never changes even after the student's foci or plan are
later edited. There is no meeting edit beyond the summary; the rating accordion, its `SkillRatingTree`
frontend components, and the month-name helpers are gone. `SkillRatingResolver` stays as a generic
taxonomy utility.

---

## ADR-023 — Per-skill rating descriptions and rating-scoped solutions

**Date:** 2026-09-09
**Decision:** In Settings, every **skill** (כישור) now carries **three mandatory rating
descriptions** — one for **green**, one for **yellow**, one for **red** — authored per skill instead
of the fixed global labels (עצמאי / בהשגחה / בתלות). **Solutions are defined under a rating**:
each solution belongs to the skill's **yellow** or **red** row (green, being a strength, has no
solutions). When building a personal plan (Tab 1, sub-tab B), the solution picker for an area shows
**only the solutions whose rating matches the rating the skill was given** — a yellow-rated area
offers yellow solutions, a red-rated area offers red solutions — replacing the previous flat
per-skill solution list.

**Context:** The client asked that each skill spell out what green/yellow/red mean for that skill,
and that solutions be entered against the specific rating so the plan offers the right options for
the actual rating rather than one undifferentiated list.

**Data model:** `skills` gains three text columns `green_text` / `yellow_text` / `red_text`
(nullable at the DB level, `default=""`); presence of all three is **enforced at the application
boundary** — `SkillCreateRequest.ratings` (a `SkillRatingsInput` DTO) and `SkillUpdateRequest`
require non-empty text for each, so a skill cannot be saved or edited without all three. `solutions`
gains a `rating` column (`MeetingRating`), constrained to **yellow/red** by a validator on
`SolutionCreateRequest`. `ProgramPlanService` rejects a chosen solution whose `rating` does not match
the area's rating. The taxonomy tree exposes the three texts on each skill node and the rating on
each solution node; the foci rating form (`FocusRatingRow`) shows the per-skill text (falling back to
the global label when empty), and `PlanForm` filters solutions by the area rating. Migration
`0027_skill_rating_solutions` adds the columns; since the prototype holds demo data only, the demo
seeder was rebuilt to the new shape (three descriptions per skill, each solution tagged yellow/red)
and a database reset reseeds it — no data conversion.

**Alternatives:** A normalized `skill_rating` child table — rejected; the ratings are a fixed set of
three, so three columns plus a request DTO are simpler and still typed. Assigning existing flat
solutions to yellow in the migration — rejected in favour of reset-and-reseed, as the prototype
carries only demo data. Showing all of a skill's solutions regardless of rating — rejected; the
client explicitly wanted the picker scoped to the chosen rating.

**Consequences:** Managers author richer, skill-specific rating guidance, and the plan picker is
tighter. Tab 1's foci document is unchanged in shape (still green = strength, yellow/red = area to
strengthen, no solutions in the foci itself — ADR-021); only the **taxonomy definition** and the
plan's **solution sourcing** changed. Green never carries solutions.

---

## ADR-024 — Tab 3 (Social-worker note) becomes a dated, archivable series with a report

**Date:** 2026-09-09
**Decision:** The social-worker note is no longer a single note per student edited in place. Each
save now records a **new dated entry** (the manager picks `note_date`, defaulting to today) that is
**appended to a history**; the tab lists all entries newest-first. A manager may **edit an entry's
text** (the date and authorship stay) and **delete** an entry — deletion is **archive-only**
(soft-delete, ADR-013): the entry is hidden from the list and the reports but retained in the
database and audit log. Every entry exports to a **per-entry PDF**, and the tab offers a **combined
report** of all the student's social-worker summaries (both server-side WeasyPrint, ADR-015), each
entry showing its date and author with the student's name in the header. Access is unchanged
(manager writes; instructor reads; professional teacher blocked — ADR-008/ADR-009).

This **supersedes the single-note shape of Tab 3** (one `social_notes` row per student, upserted in
place).

**Context:** The client asked that the social worker add a note each time, that the date be kept,
that the full history be preserved, and that a report of all the social-worker summaries can be
produced — the same dated-history + PDF pattern already used by Tab 2 (ADR-022) and the Tab 1 plan
(ADR-021).

**Data model:** the old `social_notes` table (PK `student_id`) is **dropped** and replaced by
`social_note_entries` (migration `0030_social_note_entries`): `id`, `student_id`, `note_date`
(Date), `content` (Text), `author_id`, `created_at`, `updated_at`, and soft-delete columns
`is_archived` / `archived_at` / `archived_by`. It is `TenantScoped` with the composite
`(student_id, institution_id)` foreign key and `(id, institution_id)` uniqueness, matching the
`program_plans` / `team_meetings` precedent. `SocialNoteService` exposes `report` (student name +
non-archived entries), `create`, `update` (content only), `archive`, and `entry_report` (single
entry for its PDF); author names resolve through `UserRepository`. Entries are audited under
`entity_type="social_note"` (create + update + archive). Since the prototype holds demo data only,
the migration rebuilds cleanly with no data conversion and the demo seeder now writes two dated
entries.

**Alternatives:** Version the note in place like the Tab 1 plan (keep one "current" note, push prior
versions to history) — rejected; the client described adding a note *each time*, i.e. an append-only
log of distinct dated entries, not successive versions of one document. Hard-delete an entry —
rejected; ADR-013 makes deletion archive-only across the app so history and the audit trail survive.
Omit the student name from the report to match the plan/meeting PDFs — rejected; the client asked the
report to carry the student and the author of each note.

**Consequences:** Tab 3 gains create/edit/delete-per-entry and two PDF exports; the old single
free-text box (`PUT /social-note`, `SocialNoteUpsertRequest`) is gone, replaced by
`POST` / `PATCH /{id}` / `POST /{id}/archive` / `GET` (report) / `GET /pdf` / `GET /{id}/pdf`.

---

## ADR-025 — Instructors write Tab 1 for their own workshop; the workshop list is scoped per role

**Decision:** An **instructor** may now **create and edit Tab 1** (both the foci document and the
personal plans) for **students in their own workshop**. Managers still write any student's Tab 1;
professional teachers stay read-only. This **relaxes the "manager only" write of ADR-021** — foci
(`PUT /students/{id}/program`) and plans (`POST /students/{id}/program/plans`) now accept
`ManagerOrInstructor` instead of `Manager`.

Separately, **`GET /workshops` is now scoped by role**: an instructor receives **only their own
workshop**, while managers and professional teachers (who see every student) receive the full list.

**Context:** The client asked that an instructor be able to build the promotion plans for the
students in her workshop, not only read them. Because a personal plan is derived from the latest
foci's areas to strengthen (a plan without foci is rejected, ADR-021), enabling plan creation
requires enabling foci creation too — so both sub-tabs of Tab 1 are opened together.

**Scope enforcement (server-side, the security boundary):** write access rides the existing
`StudentAccessScope` already used for reads. `StudentAccessPolicy.scope_for` returns the
instructor's single `workshop_id`, and `StudentAccessGuard.require` answers **404** (not 403) when a
student is outside the caller's scope — so an instructor writing a plan for another workshop's
student is indistinguishable from that student not existing, consistent with the tenant-isolation
rule (ADR-018) and rule 7. No change was needed in the program/plan services; only the route
dependency changed, because the scope was already threaded through `service.upsert` / `service.create`.

**Workshop-list leak fix:** `GET /workshops` previously returned every active workshop in the
institution to any authenticated user, so the frontend rendered a filter chip per workshop and an
instructor saw the *names* of workshops that were not hers even though her student list was empty of
them. `WorkshopService.list_active` now takes a `StudentAccessScope` and drops workshops the scope
does not permit; the route derives the scope from the caller. The frontend needs no change — the
chips simply reduce to the instructor's own workshop.

**Frontend:** `permissions.canWriteProgram` becomes `manager || instructor` to match the backend, so
the "יצירת/עריכת מוקדים" and "יצירת תוכנית" buttons appear for an instructor on her own students.

**Alternatives:** Open only the personal plan and keep foci manager-authored — rejected; the plan
cannot be created without foci, so the instructor would still depend on a manager and could not
"create plans" autonomously. Filter the workshop chips on the frontend only — rejected; the names
would still cross the wire, violating server-side enforcement (rule 7).

**Consequences:** Instructors gain autonomous Tab 1 authoring for their workshop; the audit log now
records instructor actors on program/plan changes. Professional-teacher and cross-workshop access are
unchanged (still read-only / 404).

---

## Open / deferred items (not yet ADRs)
- **Tab 4 extra sections** — the manager builds the headings/sub-headings themselves in Settings
  (ADR-011 mechanism implemented); no fixed names needed.
- **Login/student-screen design variation** — pick among the design's variations (frontend).


_Resolved: Hebrew font = **Heebo** default (ADR-016); email provider = **Gmail SMTP** (ADR-014);
new-institution template, institution fields, manager access recovery and multi-institution
password reset (ADR-018 follow-ups)._
