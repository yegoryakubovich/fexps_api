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


from app.tasks import celery_app
from app.utils.decorators.celery_async import celery_sync


@celery_app.task()
def request_state_waiting_check_smart_start():
    name = 'request_state_waiting_check'
    actives = celery_app.control.inspect().active()
    for worker in actives:
        for task in actives[worker]:
            if task['name'] == name:
                return
    request_state_waiting_check.apply_async()


@celery_app.task(name='request_state_waiting_check')
@celery_sync
async def request_state_waiting_check():
    # request_state_waiting_check.apply_async()
    pass
