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


from sqlalchemy import Column, BigInteger, Boolean, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class RequestRequisiteTypes:
    BLACKLIST = 'blacklist'


class RequestRequisite(Base):
    __tablename__ = 'requests_requisites'

    id = Column(BigInteger, primary_key=True)
    request_id = Column(BigInteger, ForeignKey('requests.id', ondelete='SET NULL'), nullable=True)
    request = relationship('Request', foreign_keys=request_id, uselist=False, lazy='selectin')
    requisite_id = Column(BigInteger, ForeignKey('requisites.id', ondelete='SET NULL'), nullable=True)
    requisite = relationship('Requisite', foreign_keys=requisite_id, uselist=False, lazy='selectin')
    type = Column(String(length=16))
    is_deleted = Column(Boolean, default=False)
