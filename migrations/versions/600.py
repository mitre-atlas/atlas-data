"""Baseline the ATLAS 6.0 database schema.

Revision ID: 600
Revises:
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "600"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "atlas_objects",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("references", sa.JSON(), nullable=True),
        sa.Column("created_date", sa.Date(), nullable=False),
        sa.Column("modified_date", sa.Date(), nullable=False),
        sa.Column("object_type", sa.String(length=10), nullable=False),
        sa.PrimaryKeyConstraint("id", "version"),
    )
    op.create_table(
        "format_version",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("created_date", sa.Date(), nullable=False),
        sa.Column("modified_date", sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "versions",
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("base_version", sa.String(), nullable=True),
        sa.Column("created_date", sa.Date(), nullable=False),
        sa.Column("modified_date", sa.Date(), nullable=False),
        sa.Column("publish_date", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("version"),
    )
    op.create_table(
        "case_studies",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("type", sa.String(length=8), nullable=False),
        sa.Column("actor", sa.String(), nullable=False),
        sa.Column("target", sa.String(), nullable=False),
        sa.Column("reporter", sa.String(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("date_granularity", sa.String(length=5), nullable=False),
        sa.ForeignKeyConstraint(
            ["id", "version"],
            ["atlas_objects.id", "atlas_objects.version"],
        ),
        sa.PrimaryKeyConstraint("id", "version"),
    )
    op.create_table(
        "collections",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id", "version"],
            ["atlas_objects.id", "atlas_objects.version"],
        ),
        sa.PrimaryKeyConstraint("id", "version"),
    )
    op.create_index(
        "idx_collections_version_unique",
        "collections",
        ["version"],
        unique=True,
    )
    op.create_table(
        "matrices",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id", "version"],
            ["atlas_objects.id", "atlas_objects.version"],
        ),
        sa.PrimaryKeyConstraint("id", "version"),
    )
    op.create_table(
        "mitigations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("lifecycle_phases", sa.JSON(), nullable=True),
        sa.Column("categories", sa.JSON(), nullable=True),
        sa.Column("attack_reference", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id", "version"],
            ["atlas_objects.id", "atlas_objects.version"],
        ),
        sa.PrimaryKeyConstraint("id", "version"),
    )
    op.create_table(
        "relationships",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("target", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("relationship_type", sa.String(length=11), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("extra_fields", sa.JSON(), nullable=True),
        sa.CheckConstraint(
            "source != target",
            name="ck_relationship_source_not_target",
        ),
        sa.ForeignKeyConstraint(
            ["source", "version"],
            ["atlas_objects.id", "atlas_objects.version"],
        ),
        sa.ForeignKeyConstraint(
            ["target", "version"],
            ["atlas_objects.id", "atlas_objects.version"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_employs_unique",
        "relationships",
        ["source", "target", "version", "relationship_type", "extra_fields"],
        unique=True,
        sqlite_where=sa.text("relationship_type = 'EMPLOYS'"),
    )
    op.create_index(
        "idx_unique_non_employs",
        "relationships",
        ["source", "target", "version", "relationship_type"],
        unique=True,
        sqlite_where=sa.text("relationship_type != 'EMPLOYS'"),
    )
    op.create_index(
        "ix_relationships_relationship_type",
        "relationships",
        ["relationship_type"],
        unique=False,
    )
    op.create_table(
        "tactics",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("attack_reference", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id", "version"],
            ["atlas_objects.id", "atlas_objects.version"],
        ),
        sa.PrimaryKeyConstraint("id", "version"),
    )
    op.create_table(
        "techniques",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("maturity", sa.String(length=12), nullable=False),
        sa.Column("platforms", sa.JSON(), nullable=True),
        sa.Column("attack_reference", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id", "version"],
            ["atlas_objects.id", "atlas_objects.version"],
        ),
        sa.PrimaryKeyConstraint("id", "version"),
    )


def downgrade() -> None:
    op.drop_table("techniques")
    op.drop_table("tactics")
    op.drop_index("ix_relationships_relationship_type", table_name="relationships")
    op.drop_index("idx_unique_non_employs", table_name="relationships")
    op.drop_index("idx_employs_unique", table_name="relationships")
    op.drop_table("relationships")
    op.drop_table("mitigations")
    op.drop_table("matrices")
    op.drop_index("idx_collections_version_unique", table_name="collections")
    op.drop_table("collections")
    op.drop_table("case_studies")
    op.drop_table("versions")
    op.drop_table("format_version")
    op.drop_table("atlas_objects")
