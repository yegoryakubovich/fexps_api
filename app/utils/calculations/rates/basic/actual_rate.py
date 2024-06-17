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


import datetime

from app.db.models import Rate, RatePair
from config import settings


async def check_actual_rate(rate: [Rate, RatePair]) -> bool:
    rate_date = rate.created_at.replace(tzinfo=datetime.timezone.utc)
    date_now = datetime.datetime.now(tz=datetime.timezone.utc)
    date_delta = datetime.timedelta(minutes=settings.rate_actual_minutes)
    date_check = date_now - date_delta
    if rate_date < date_check:
        return False
    return True