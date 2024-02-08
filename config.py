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


from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_port: int

    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_name: str

    redis_host: str
    redis_port: int
    redis_user: str
    redis_password: str

    root_token: str
    debug: int
    wallet_max_count: int
    wallet_max_value: int

    version: str = '0.1'
    path_articles: str = 'assets/articles'
    path_texts_packs: str = 'assets/texts_packs'
    path_images: str = 'assets/images'

    items_per_page: int = 10
    request_waiting_check: int = 2
    request_rate_reservation_minutes: int = 60

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
