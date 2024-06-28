#
# (c) 2024, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from sqlalchemy import Column, BigInteger, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class WalletBanRequisite(Base):
    __tablename__ = 'wallets_bans_requisites'

    id = Column(BigInteger, primary_key=True)
    wallet_ban_id = Column(BigInteger, ForeignKey('wallets_bans.id', ondelete='SET NULL'))
    wallet_ban = relationship('WalletBan', foreign_keys=wallet_ban_id, uselist=False, lazy='selectin')
    requisite_id = Column(BigInteger, ForeignKey('requisites.id', ondelete='SET NULL'))
    requisite = relationship('Requisite', foreign_keys=requisite_id, uselist=False, lazy='selectin')
    is_deleted = Column(Boolean, default=False)
