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
    api_port: int
    tasks_flower_port: int

    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_name: str

    redis_host: str
    redis_port: int
    redis_user: str
    redis_password: str

    flower_user: str
    flower_password: str

    telegram_token: str
    telegram_chat_id: int
    telegram_manager: str
    telegram_about: str
    telegram_info: str
    telegram_reviews: str
    telegram_rate_pairs: list = [
        ('rub', 'usd'),
        ('usd', 'rub'),
        ('usdt', 'usd'),
        ('usd', 'usdt'),
    ]

    root_token: str
    file_url: str
    chat_url: str
    sync_db_url: str
    sync_db_table_name: str
    debug: int
    wallet_max_count: int
    wallet_max_value: int

    test: bool
    test_file_url: str
    test_chat_url: str
    test_sync_db_url: str

    version: str = '0.1'
    path_texts_packs: str = 'assets/texts_packs'
    path_files: str = 'assets/files'
    path_telegram: str = 'assets/telegram'

    items_per_page: int = 10
    request_waiting_check: int = 5
    request_rate_confirmed_minutes: int = 60
    datetime_format: str = '%d-%m-%y %H:%M'

    model_config = SettingsConfigDict(env_file='.env')

    def get_mysql_host(self) -> str:
        if self.test:
            # return '192.168.31.40'
            return '127.0.0.1'
        return self.mysql_host

    def get_file_url(self):
        if self.test:
            return self.test_file_url
        return self.file_url

    def get_chat_url(self):
        if self.test:
            return self.test_chat_url
        return self.chat_url

    def get_sync_db_url(self):
        if self.test:
            return self.test_sync_db_url
        return self.sync_db_url


settings = Settings()
