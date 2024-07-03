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


import asyncio
import logging

from addict import Dict
from gspread import Spreadsheet

from app.tasks.permanents.utils.fexps_api_client import fexps_api_client
from app.tasks.permanents.utils.google_sheets_api_client import google_sheets_api_client

PREFIXES = [
    'permission_',
    'role_',
    'commission_pack_',
    'contact_',
    'method_',
    'method_field_',
    'method_input_field_',
]
DEFAULT_LANGUAGE = 'eng'


async def sync_texts(table: Spreadsheet):
    logging.info('start update texts')
    is_changed = False

    languages = [language.id_str for language in await fexps_api_client.client.languages.get_list()]

    sheet_texts = await google_sheets_api_client.get_sheet_by_table_and_name(table=table, name='texts')
    rows_texts = await google_sheets_api_client.get_rows(sheet=sheet_texts)

    sheet_error = await google_sheets_api_client.get_sheet_by_table_and_name(table=table, name='errors')
    rows_error = await google_sheets_api_client.get_rows(sheet=sheet_error)

    texts_table = rows_texts + [
        Dict(
            key=f'error_{error.code}',
            **{
                key: value for key, value in error.items() if key not in ['code', 'class']
            },
        ) for error in rows_error
    ]

    sheet_keys = [row.get('key') for row in texts_table]

    texts = await fexps_api_client.admin.texts.get_list()
    texts_keys = [text.key for text in texts]
    texts_api = Dict(
        **{
            text.key: dict(
                default_value=text.value_default,
                translations={
                    translation.language: translation.value for translation in text.translations
                },
            ) for text in texts
        }
    )
    match = list(set(sheet_keys) & set(texts_keys))

    need_create = [key for key in sheet_keys if key not in match]
    need_delete = [key for key in texts_keys if key not in match and not key.startswith(tuple(PREFIXES))]

    # Global block

    # Delete
    for key in need_delete:
        await fexps_api_client.admin.texts.delete(
            key=key,
            create_text_pack=False,
        )
        is_changed = True

    for text_table in texts_table:
        key = text_table.key
        text_api = texts_api.get(key)

        skip_update = False
        # Create
        if key in need_create:
            await fexps_api_client.admin.texts.create(
                key=key,
                value_default=text_table.get(DEFAULT_LANGUAGE),
                create_text_pack=False,
            )
            skip_update = True
            is_changed = True

        # Update
        if not skip_update:
            current_value_default = text_api.get('default_value')
            new_value_default = text_table.get(DEFAULT_LANGUAGE)

            if current_value_default != new_value_default:
                await fexps_api_client.admin.texts.update(
                    key=key,
                    value_default=new_value_default,
                    create_text_pack=False,
                )
                is_changed = True

        # Translations block
        current_translations = text_api.translations if text_api else {}
        new_translations = text_table.copy()
        new_translations.pop('key')
        match_translations = list(set(current_translations.keys()) & set(new_translations.keys()))
        need_create_translations = [key for key in new_translations.keys() if key not in match_translations]
        need_delete_translations = [key for key in current_translations.keys() if key not in match_translations]

        # Delete translation
        for language_delete in need_delete_translations:
            await fexps_api_client.admin.texts.translations.delete(
                text_key=key,
                language=language_delete,
                create_text_pack=False,
            )
            is_changed = True
            continue

        for language in languages:
            # Create translation
            if language in need_create_translations:
                await fexps_api_client.admin.texts.translations.create(
                    text_key=key,
                    language=language,
                    value=new_translations.get(language),
                    create_text_pack=False,
                )
                is_changed = True
                continue

            # Update translation
            current_translation = current_translations.get(language, None)
            new_translation = new_translations.get(language, None)
            if current_translation != new_translation:
                is_changed = True
                await fexps_api_client.admin.texts.translations.update(
                    text_key=key,
                    language=language,
                    value=new_translation,
                    create_text_pack=False,
                )

    if is_changed:
        await fexps_api_client.admin.texts.packs.create_all()
    logging.info('end update texts')
    await asyncio.sleep(0.5)
