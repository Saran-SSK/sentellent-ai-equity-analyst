"""add user_company_views table

Revision ID: 5b4db90e4f3a
Revises: ab27ea2f8c6d
Create Date: 2026-08-03 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "5b4db90e4f3a"
down_revision: Union[str, Sequence[str], None] = "ab27ea2f8c6d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_company_views",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column(
            "viewed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_company_views_id"), "user_company_views", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_user_company_views_symbol"),
        "user_company_views",
        ["symbol"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_company_views_user_id"),
        "user_company_views",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_user_company_views_user_id"), table_name="user_company_views"
    )
    op.drop_index(op.f("ix_user_company_views_symbol"), table_name="user_company_views")
    op.drop_index(op.f("ix_user_company_views_id"), table_name="user_company_views")
    op.drop_table("user_company_views")
