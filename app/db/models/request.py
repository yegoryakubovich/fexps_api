#
# (c) 2023, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
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


from sqlalchemy import Column, BigInteger, Boolean, ForeignKey, Double, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class RequestTypes:
    INPUT = 'input'
    OUTPUT = 'output'
    ALL = 'all'

    choices = [INPUT, OUTPUT, ALL]


class Request(Base):
    __tablename__ = 'requests'

    id = Column(BigInteger, primary_key=True)
    wallet_id = Column(BigInteger, ForeignKey('wallets.id', ondelete='SET NULL'), nullable=True)
    wallet = relationship('Wallet', uselist=False, lazy='selectin')
    type = Column(String(length=8))
    input_method_id = Column(BigInteger, ForeignKey('methods.id', ondelete='SET NULL'), nullable=True)
    input_method = relationship('Method', foreign_keys=input_method_id, uselist=False, lazy='selectin')

    input_value = Column(BigInteger, nullable=True)
    input_rate = Column(Double, nullable=True)
    value = Column(BigInteger, nullable=True)
    rate = Column(Double, nullable=True)
    output_value = Column(BigInteger, nullable=True)
    output_rate = Column(Double, nullable=True)

    output_method_id = Column(BigInteger, ForeignKey('methods.id', ondelete='SET NULL'), nullable=True)
    output_method = relationship('Method', foreign_keys=output_method_id, uselist=False, lazy='selectin')
    output_requisite_data_id = Column(BigInteger, ForeignKey('requisites_datas.id', ondelete='SET NULL'), nullable=True)
    output_requisite_data = relationship('RequisiteData', foreign_keys=output_requisite_data_id,
                                         uselist=False, lazy='selectin')
    is_deleted = Column(Boolean, default=False)
