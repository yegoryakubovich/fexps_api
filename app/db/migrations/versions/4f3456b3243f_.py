"""empty message

Revision ID: 4f3456b3243f
Revises: f6572fcf908d
Create Date: 2024-07-22 19:07:38.351276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '4f3456b3243f'
down_revision: Union[str, None] = 'f6572fcf908d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('telegrams_posts', sa.Column('data', sa.JSON(), nullable=True))
    op.drop_column('telegrams_posts', 'message_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('telegrams_posts', sa.Column('message_id', mysql.BIGINT(), autoincrement=False, nullable=True))
    op.drop_column('telegrams_posts', 'data')
    # ### end Alembic commands ###
