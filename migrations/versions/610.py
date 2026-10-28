"""Add entities, software, version ownership, and case-study ranges for ATLAS 6.1.

Revision ID: 610
Revises: 600
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "610"
down_revision: str | None = "600"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    connection = op.get_bind()
    orphan = connection.execute(
        sa.text(
            "SELECT DISTINCT version FROM atlas_objects "
            "WHERE version NOT IN (SELECT version FROM versions) LIMIT 1"
        )
    ).first()
    if orphan is not None:
        raise RuntimeError(
            f"Objects reference missing version {orphan[0]!r}. "
            "Create the corresponding version record before upgrading."
        )

    with op.batch_alter_table("atlas_objects") as batch_op:
        batch_op.create_foreign_key(
            "fk_atlas_objects_version", "versions", ["version"], ["version"]
        )

    with op.batch_alter_table("relationships") as batch_op:
        batch_op.alter_column(
            "relationship_type",
            existing_type=sa.String(length=11),
            type_=sa.String(length=13),
            existing_nullable=False,
        )

    with op.batch_alter_table("case_studies") as batch_op:
        batch_op.alter_column(
            "actor", existing_type=sa.String(), existing_nullable=False, nullable=True
        )
        batch_op.alter_column(
            "date",
            new_column_name="start_date",
            existing_type=sa.Date(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "date_granularity",
            new_column_name="start_date_granularity",
            existing_type=sa.String(length=5),
            existing_nullable=False,
        )
        batch_op.add_column(sa.Column("end_date", sa.Date(), nullable=True))
        batch_op.add_column(
            sa.Column("end_date_granularity", sa.String(length=5), nullable=True)
        )
        batch_op.create_check_constraint(
            "ck_case_studies_end_date_pair",
            "(end_date IS NULL AND end_date_granularity IS NULL) OR "
            "(end_date IS NOT NULL AND end_date_granularity IS NOT NULL)",
        )
    op.execute(
        sa.text(
            "UPDATE case_studies SET end_date = start_date, "
            "end_date_granularity = start_date_granularity"
        )
    )

    op.create_table(
        "entities",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("entity_type", sa.String(length=16), nullable=False),
        sa.Column("associated_entities", sa.JSON(), nullable=True),
        sa.Column("attack_reference", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id", "version"],
            ["atlas_objects.id", "atlas_objects.version"],
        ),
        sa.PrimaryKeyConstraint("id", "version"),
    )
    op.create_table(
        "software",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("software_type", sa.String(length=7), nullable=False),
        sa.Column("software_categories", sa.JSON(), nullable=True),
        sa.Column("aliases", sa.JSON(), nullable=True),
        sa.Column("attack_reference", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id", "version"],
            ["atlas_objects.id", "atlas_objects.version"],
        ),
        sa.PrimaryKeyConstraint("id", "version"),
    )
    op.execute(
        sa.text("UPDATE format_version SET version = '6.1.0' WHERE version = '6.0.0'")
    )


def downgrade() -> None:
    # Version 600 requires an actor. Do not fabricate attribution on downgrade.
    if op.get_bind().execute(
        sa.text("SELECT 1 FROM case_studies WHERE actor IS NULL LIMIT 1")
    ).first() is not None:
        raise RuntimeError("Populate null case-study actors before downgrading to 600")

    if op.get_bind().execute(
        sa.text(
            "SELECT 1 FROM case_studies WHERE end_date IS NULL "
            "OR end_date != start_date "
            "OR end_date_granularity != start_date_granularity LIMIT 1"
        )
    ).first() is not None:
        raise RuntimeError("Case-study date ranges cannot be represented in 600")

    with op.batch_alter_table("case_studies") as batch_op:
        batch_op.drop_constraint("ck_case_studies_end_date_pair", type_="check")
        batch_op.drop_column("end_date")
        batch_op.drop_column("end_date_granularity")
        batch_op.alter_column(
            "start_date",
            new_column_name="date",
            existing_type=sa.Date(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "start_date_granularity",
            new_column_name="date_granularity",
            existing_type=sa.String(length=5),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "actor", existing_type=sa.String(), existing_nullable=True, nullable=False
        )

    with op.batch_alter_table("atlas_objects") as batch_op:
        batch_op.drop_constraint("fk_atlas_objects_version", type_="foreignkey")

    op.execute(
        sa.text(
            "DELETE FROM relationships "
            "WHERE relationship_type IN ('ATTRIBUTED_TO', 'REPORTED_BY', 'IMPLEMENTS', 'USES')"
        )
    )
    op.execute(sa.text("DELETE FROM software"))
    op.execute(sa.text("DELETE FROM entities"))
    op.execute(
        sa.text("DELETE FROM atlas_objects WHERE object_type IN ('ENTITY', 'SOFTWARE')")
    )
    op.drop_table("software")
    op.drop_table("entities")

    with op.batch_alter_table("relationships") as batch_op:
        batch_op.alter_column(
            "relationship_type",
            existing_type=sa.String(length=13),
            type_=sa.String(length=11),
            existing_nullable=False,
        )

    op.execute(
        sa.text("UPDATE format_version SET version = '6.0.0' WHERE version = '6.1.0'")
    )
