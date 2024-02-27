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


from celery.app import Celery

from config import settings


redis_url = f'redis://{settings.redis_user}:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}'
celery_app = Celery(__name__, broker=redis_url, backend=redis_url)
celery_app.control.purge()

celery_app.autodiscover_tasks(['app.tasks.schedule'])
