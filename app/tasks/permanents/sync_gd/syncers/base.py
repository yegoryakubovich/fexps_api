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


from gspread import Spreadsheet

from ..utils.google_sheets_api_client import google_sheets_api_client


async def sync_base(
        table: Spreadsheet,
        sheet_name,
        api_method_get_list,
        api_method_delete,
        api_method_create,
        key_name='id_str',
):
    sheet = await google_sheets_api_client.get_sheet_by_table_and_name(table=table, name=sheet_name)
    table = await google_sheets_api_client.get_rows(sheet=sheet)
    table_ids_str = [obj.get(key_name) for obj in table]

    api = await api_method_get_list()
    api_ids_str = [obj.get(key_name) for obj in api]

    match = list(set(api_ids_str) & set(table_ids_str))
    need_create = [id_str for id_str in table_ids_str if id_str not in match]
    need_delete = [id_str for id_str in api_ids_str if id_str not in match]

    if key_name in ['id_str']:
        for id_str in need_delete:
            await api_method_delete(
                id_str=id_str,
            )

    for obj in table:
        id_str = obj.get(key_name)
        if id_str in need_create:

            # For roles
            if key_name not in ['id_str']:
                if len(api) == 0:
                    await api_method_create(obj=obj)
                break

            await api_method_create(obj=obj)
