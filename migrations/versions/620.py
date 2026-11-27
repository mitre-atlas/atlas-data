"""Add Research and Hardware and rename Enterprise to Cyber for ATLAS 6.2.

Revision ID: 620
Revises: 610
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "620"
down_revision: str | None = "610"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

techniques = sa.table(
    "techniques",
    sa.column("id", sa.String()),
    sa.column("version", sa.String()),
    sa.column("platforms", sa.JSON()),
)


def rename_platform(old: str, new: str) -> None:
    connection = op.get_bind()
    for row in connection.execute(sa.select(techniques)).all():
        if row.platforms is not None and old in row.platforms:
            connection.execute(
                techniques.update()
                .where(techniques.c.id == row.id, techniques.c.version == row.version)
                .values(
                    platforms=[
                        new if value == old else value for value in row.platforms
                    ]
                )
            )


def upgrade() -> None:
    # Research uses the existing unconstrained VARCHAR(8) case-study type column.
    rename_platform("Enterprise", "Cyber")
    op.execute(
        sa.text("UPDATE format_version SET version = '6.2.0' WHERE version = '6.1.0'")
    )


def downgrade() -> None:
    if op.get_bind().execute(
        sa.text("SELECT 1 FROM case_studies WHERE type = 'RESEARCH' LIMIT 1")
    ).first() is not None:
        raise RuntimeError("Research case studies cannot be represented in 610")
    for platforms in op.get_bind().execute(sa.select(techniques.c.platforms)).scalars():
        if platforms is not None and "Hardware" in platforms:
            raise RuntimeError("Hardware platforms cannot be represented in 610")
    rename_platform("Cyber", "Enterprise")
    op.execute(
        sa.text("UPDATE format_version SET version = '6.1.0' WHERE version = '6.2.0'")
    )
