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


from configparser import ConfigParser


config = ConfigParser()
config.read('config.ini')

config_db = config['db']

MYSQL_HOST = config_db['host']
MYSQL_PORT = int(config_db['port'])
MYSQL_USER = config_db['user']
MYSQL_PASSWORD = config_db['password']
MYSQL_NAME = config_db['name']

config_settings = config['settings']

WALLET_MAX_COUNT = int(config_settings['wallet_max_count'])
WALLET_MAX_VALUE = float(config_settings['wallet_max_value'])
ITEMS_PER_PAGE = int(config_settings['items_per_page'])

VERSION = '0.1'
PATH_TEXTS_PACKS = 'assets/texts_packs'
