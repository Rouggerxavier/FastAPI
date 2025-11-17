"""add preco to pedidos

Revision ID: 5e1f2d9d3a4b
Revises: 3a9e21b4620e
Create Date: 2025-11-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e1f2d9d3a4b'
down_revision: Union[str, Sequence[str], None] = '3a9e21b4620e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('pedidos', sa.Column('preco', sa.Float(), nullable=False, server_default='0'))
    op.alter_column('pedidos', 'preco', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('pedidos', 'preco')