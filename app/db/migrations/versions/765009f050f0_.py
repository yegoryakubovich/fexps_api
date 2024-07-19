"""empty message

Revision ID: 765009f050f0
Revises: 87d8a3f28533
Create Date: 2024-07-18 19:50:44.592039

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '765009f050f0'
down_revision: Union[str, None] = '87d8a3f28533'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rates_pairs', sa.Column('commission_pack_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key(None, 'rates_pairs', 'commissions_packs', ['commission_pack_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'rates_pairs', type_='foreignkey')
    op.drop_column('rates_pairs', 'commission_pack_id')
    # ### end Alembic commands ###