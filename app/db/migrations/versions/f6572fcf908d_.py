"""empty message

Revision ID: f6572fcf908d
Revises: 765009f050f0
Create Date: 2024-07-22 17:21:45.328014

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'f6572fcf908d'
down_revision: Union[str, None] = '765009f050f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('commissions_packs', sa.Column('telegram_type', sa.String(length=32), nullable=True))
    op.drop_column('commissions_packs', 'filename')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('commissions_packs', sa.Column('filename', mysql.VARCHAR(charset='utf8mb4', collation='utf8mb4_0900_ai_ci', length=32), nullable=True))
    op.drop_column('commissions_packs', 'telegram_type')
    # ### end Alembic commands ###
