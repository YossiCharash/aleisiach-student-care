"""flatten skills onto labels, removing the sub_label layer (Tab 1)

Revision ID: 0029_flatten_skills_to_labels
Revises: 0028_normalize_rating_case
Create Date: 2026-09-09

Collapses the sub_label layer out of the taxonomy. Each skill moves to the label
its sub_label belonged to, and every group that was stored as three rating rows
("עצמאי" / "תיווך/השגחה" / "תלותי" crammed into ``name``) is consolidated into a
single skill row whose green_text / yellow_text / red_text are filled and whose
name is the sub_label's name. References to the removed rows are re-pointed to the
surviving row first, so no foreign key is orphaned. On an empty database (CI, a
fresh install) every data step is a no-op and only the schema change applies.

Every step guards on its object already existing, so the migration is re-runnable
against a database where an earlier interrupted attempt left ``skills.label_id`` in
place without stamping the revision — the flatten only runs while ``sub_labels`` is
still present.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0029_flatten_skills_to_labels"
down_revision: str | None = "0028_normalize_rating_case"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_REFERENCING_TABLES: tuple[str, ...] = (
    "solutions",
    "program_entries",
    "program_plan_entries",
    "meeting_foci_entries",
    "meeting_plan_entries",
)

_SURVIVOR = """
CREATE TEMP TABLE _skill_survivor ON COMMIT DROP AS
SELECT DISTINCT ON (s.sub_label_id, s.institution_id)
       s.id AS survivor_id, s.sub_label_id, s.institution_id
FROM skills s
ORDER BY s.sub_label_id, s.institution_id, s."order", s.id
"""

_REMAP = """
CREATE TEMP TABLE _skill_remap ON COMMIT DROP AS
SELECT s.id AS old_id, v.survivor_id, s.institution_id
FROM skills s
JOIN _skill_survivor v
  ON v.sub_label_id = s.sub_label_id AND v.institution_id = s.institution_id
"""

_GROUP_VALUES = """
CREATE TEMP TABLE _group_values ON COMMIT DROP AS
SELECT
    s.sub_label_id,
    s.institution_id,
    sl.label_id AS parent_label_id,
    sl.name     AS sublabel_name,
    MAX(CASE WHEN btrim(s.name) ~ '^עצמאי'         THEN s.name END) AS g_from_name,
    MAX(CASE WHEN btrim(s.name) ~ '^(תיווך|השגחה)' THEN s.name END) AS y_from_name,
    MAX(CASE WHEN btrim(s.name) ~ '^תלותי'         THEN s.name END) AS r_from_name,
    MAX(NULLIF(s.green_text, ''))  AS g_existing,
    MAX(NULLIF(s.yellow_text, '')) AS y_existing,
    MAX(NULLIF(s.red_text, ''))    AS r_existing
FROM skills s
JOIN sub_labels sl
  ON sl.id = s.sub_label_id AND sl.institution_id = s.institution_id
GROUP BY s.sub_label_id, s.institution_id, sl.label_id, sl.name
"""

_REPOINT = """
UPDATE {table} t SET skill_id = m.survivor_id
FROM _skill_remap m
WHERE t.skill_id = m.old_id AND t.institution_id = m.institution_id AND m.old_id <> m.survivor_id
"""

_FILL_SURVIVOR = """
UPDATE skills t
SET label_id    = g.parent_label_id,
    name        = g.sublabel_name,
    green_text  = COALESCE(g.g_existing, g.g_from_name, ''),
    yellow_text = COALESCE(g.y_existing, g.y_from_name, ''),
    red_text    = COALESCE(g.r_existing, g.r_from_name, '')
FROM _skill_survivor v
JOIN _group_values g
  ON g.sub_label_id = v.sub_label_id AND g.institution_id = v.institution_id
WHERE t.id = v.survivor_id
"""

_DELETE_REDUNDANT = """
DELETE FROM skills s
USING _skill_remap m
WHERE s.id = m.old_id AND s.institution_id = m.institution_id AND m.old_id <> m.survivor_id
"""


def upgrade() -> None:
    bind = op.get_bind()
    op.execute("ALTER TABLE skills ADD COLUMN IF NOT EXISTS label_id UUID")

    sub_labels_present = (
        bind.execute(sa.text("SELECT to_regclass('public.sub_labels')")).scalar() is not None
    )
    if sub_labels_present:
        op.execute(_SURVIVOR)
        op.execute(_REMAP)
        op.execute(_GROUP_VALUES)
        for table in _REFERENCING_TABLES:
            op.execute(_REPOINT.format(table=table))
        op.execute(_FILL_SURVIVOR)
        op.execute(_DELETE_REDUNDANT)

    op.execute("ALTER TABLE skills ALTER COLUMN label_id SET NOT NULL")
    op.execute("CREATE INDEX IF NOT EXISTS ix_skills_label_id ON skills (label_id)")
    op.execute("ALTER TABLE skills DROP CONSTRAINT IF EXISTS fk_skills_label_institution")
    op.create_foreign_key(
        "fk_skills_label_institution",
        "skills",
        "labels",
        ["label_id", "institution_id"],
        ["id", "institution_id"],
    )

    op.execute("ALTER TABLE skills DROP CONSTRAINT IF EXISTS fk_skills_sub_label_institution")
    op.execute("DROP INDEX IF EXISTS ix_skills_sub_label_id")
    op.execute("ALTER TABLE skills DROP COLUMN IF EXISTS sub_label_id")
    op.execute("DROP TABLE IF EXISTS sub_labels")


def downgrade() -> None:
    raise NotImplementedError("flattening skills onto labels is irreversible")
