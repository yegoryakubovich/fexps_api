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


import logging


class TelegramLogger:
    def __init__(self, prefix: str):
        self.prefix = prefix

    def send(
            self,
            func: callable,
            text: str,
    ) -> None:
        log_list = [f'[{self.prefix}]']
        log_list += [text]
        func(f' '.join(log_list))

    def info(self, **kwargs) -> None:
        self.send(func=logging.info, **kwargs)

    def critical(self, **kwargs) -> None:
        self.send(func=logging.critical, **kwargs)
