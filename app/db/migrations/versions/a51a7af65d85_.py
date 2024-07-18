"""empty message

Revision ID: a51a7af65d85
Revises: 26d834736632
Create Date: 2024-07-18 15:24:50.436929

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a51a7af65d85'
down_revision: Union[str, None] = '26d834736632'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('commissions_packs', sa.Column('telegram_chat_id', sa.BigInteger(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('commissions_packs', 'telegram_chat_id')
    # ### end Alembic commands ###
