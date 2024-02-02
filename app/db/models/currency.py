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


from sqlalchemy import Column, BigInteger, String, Boolean, Integer

from app.db.base_class import Base


class Currency(Base):
    __tablename__ = 'currencies'

    id = Column(BigInteger, primary_key=True)
    id_str = Column(String(length=16))
    decimal = Column(Integer, default=2)
    rate_decimal = Column(Integer, default=2)
    div = Column(Integer, default=2)
    is_deleted = Column(Boolean, default=False)
