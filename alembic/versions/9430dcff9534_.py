"""empty message

Revision ID: 9430dcff9534
Revises: 7a9bd1446edb
Create Date: 2026-06-30 10:32:14.535759

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9430dcff9534'
down_revision: Union[str, Sequence[str], None] = '7a9bd1446edb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
