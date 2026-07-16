"""initialize database migrations

Revision ID: 17163c0638a0
Revises:
Create Date: 2026-07-15 20:42:16.639329

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "17163c0638a0"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
