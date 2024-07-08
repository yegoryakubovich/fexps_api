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

from app.tasks.permanents.sync_gd.texts import sync_texts
from app.tasks.permanents.utils.fexps_api_client import fexps_api_client
from app.tasks.permanents.utils.google_sheets_api_client import google_sheets_api_client
from config import settings
from app.tasks.permanents.sync_gd.base import sync_base
from app.tasks.permanents.sync_gd.roles_permissions import sync_roles_permissions


async def sync():
    logging.info('Start sync')

    async def create_client_text(obj):
        await fexps_api_client.admin.clients_texts.create(key=obj.get('key'), name=obj.get('name'))

    async def create_permission(obj):
        await fexps_api_client.admin.permissions.create(id_str=obj.get('id_str'), name=obj.get('name'))

    async def create_roles(obj):
        role_id = await fexps_api_client.admin.roles.create(name=obj.get('name'))
        if role_id == 1:
            await sync_roles_permissions(role_id=role_id)

    async def create_language(obj):
        await fexps_api_client.admin.languages.create(id_str=obj.get('id_str'), name=obj.get('name'))

    async def create_timezone(obj):
        await fexps_api_client.admin.timezones.create(id_str=obj.get('id_str'), deviation=obj.get('deviation'))

    async def create_currency(obj):
        await fexps_api_client.admin.currencies.create(
            id_str=obj.get('id_str'),
            decimal=obj.get('decimal'),
            rate_decimal=obj.get('rate_decimal'),
            div=obj.get('div'),
        )

    async def create_country(obj):
        await fexps_api_client.admin.countries.create(
            id_str=obj.get('id_str'),
            name=obj.get('name'),
            language_default=obj.get('language_default'),
            currency_default=obj.get('currency_default'),
            timezone_default=obj.get('timezone_default'),
        )

    table = await google_sheets_api_client.get_table_by_name(name=settings.sync_db_table_name)

    # ClientText
    await sync_base(
        table=table,
        sheet_name='ClientsTexts',
        api_method_get_list=fexps_api_client.client.clients_texts.get_list,
        api_method_delete=fexps_api_client.admin.clients_texts.delete,
        api_method_create=create_client_text,
    )

    # Permissions
    await sync_base(
        table=table,
        sheet_name='permissions',
        api_method_get_list=fexps_api_client.admin.permissions.get_list,
        api_method_delete=fexps_api_client.admin.permissions.delete,
        api_method_create=create_permission,
    )

    # Roles
    await sync_base(
        table=table,
        sheet_name='roles',
        api_method_get_list=fexps_api_client.admin.roles.get_list,
        api_method_delete=fexps_api_client.admin.roles.delete,
        api_method_create=create_roles,
        key_name='name',
    )

    # Languages
    await sync_base(
        table=table,
        sheet_name='languages',
        api_method_get_list=fexps_api_client.client.languages.get_list,
        api_method_delete=fexps_api_client.admin.languages.delete,
        api_method_create=create_language,
    )

    # Timezones
    await sync_base(
        table=table,
        sheet_name='timezones',
        api_method_get_list=fexps_api_client.client.timezones.get_list,
        api_method_delete=fexps_api_client.admin.timezones.delete,
        api_method_create=create_timezone,
    )

    # Currencies
    await sync_base(
        table=table,
        sheet_name='currencies',
        api_method_get_list=fexps_api_client.client.currencies.get_list,
        api_method_delete=fexps_api_client.admin.currencies.delete,
        api_method_create=create_currency,
    )

    # Countries
    await sync_base(
        table=table,
        sheet_name='countries',
        api_method_get_list=fexps_api_client.client.countries.get_list,
        api_method_delete=fexps_api_client.admin.countries.delete,
        api_method_create=create_country,
    )

    # Texts
    await sync_texts(table=table)
