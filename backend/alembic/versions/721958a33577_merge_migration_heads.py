"""merge migration heads

Revision ID: 721958a33577
Revises: 5f75bfe000d1, add_google_oauth_fields
Create Date: 2026-08-01 16:24:44.920846

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '721958a33577'
down_revision: Union[str, Sequence[str], None] = ('5f75bfe000d1', 'add_google_oauth_fields')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
