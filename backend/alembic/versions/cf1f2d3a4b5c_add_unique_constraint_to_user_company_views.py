"""Add unique constraint for user-company view entries.

Revision ID: cf1f2d3a4b5c
Revises: 5b4db90e4f3a
Create Date: 2026-08-03 00:01:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "cf1f2d3a4b5c"
down_revision: Union[str, Sequence[str], None] = "5b4db90e4f3a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove duplicate rows before adding unique constraint
    # Keep only the most recent row for each (user_id, symbol) pair
    op.execute("""
        DELETE FROM user_company_views
        WHERE id NOT IN (
            SELECT DISTINCT ON (user_id, symbol) id
            FROM user_company_views
            ORDER BY user_id, symbol, viewed_at DESC
        )
    """)

    # Now add the unique constraint
    op.create_unique_constraint(
        "uq_user_company_views_user_symbol",
        "user_company_views",
        ["user_id", "symbol"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_user_company_views_user_symbol",
        "user_company_views",
        type_="unique",
    )
