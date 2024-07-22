#
# (c) 2023, Yegor Yakubovich
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
import logging
from typing import Optional

from PIL import Image, ImageDraw, ImageFont
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.db.models import CommissionPack, CommissionPackValue, Method
from app.repositories import CommissionPackValueRepository, CurrencyRepository, MethodRepository, RatePairRepository
from app.utils.value import value_to_float
from config import settings

MONTH_DAY = [
    'января', 'февраля', 'марта', 'апреля', 'мая', 'июня' 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря',
]
COORDINATES_RANGES = {
    '0-9999': [[228, 313], [788, 413]],
    '10000-29999': [[228, 419], [788, 519]],
    '30000-149999': [[228, 525], [788, 625]],
    '150000-499999': [[228, 631], [788, 731]],
    '500000-0': [[228, 737], [788, 837]],
}
COORDINATES_RATES = {
    '0-9999': [[795, 313], [1125, 413]],
    '10000-29999': [[795, 419], [1125, 519]],
    '30000-149999': [[795, 525], [1125, 625]],
    '150000-499999': [[795, 631], [1125, 731]],
    '500000-0': [[795, 737], [1125, 837]],
}
RANGES = {
    '0-9999': '1-100 USD',
    '10000-29999': '100-300 USD',
    '30000-149999': '300-1500 USD',
    '150000-499999': '1500-5000 USD',
    '500000-0': 'от 5000 USD',
}
FONT_MONTSERRAT_SEMIBOLD = ImageFont.truetype(f'{settings.path_telegram}/fonts/montserrat_semibold.ttf', 50)
FONT_MONTSERRAT_REGULAR = ImageFont.truetype(f'{settings.path_telegram}/fonts/montserrat_regular.ttf', 36)
FONT_JETBRAINSMONO_REGULAR = ImageFont.truetype(f'{settings.path_telegram}/fonts/jetbrainsmono_regular.ttf', 24)


def get_post_text() -> str:
    date_now = datetime.datetime.now(tz=datetime.timezone.utc)
    return '\n'.join([
        f'С Вами Finance Express! 🐆',
        f'🗓 Наступило {date_now.day} {MONTH_DAY[date_now.month - 1]}!',
        f'Прекрасная возможность обменять деньги по ВЫГОДНОМУ курсу🤝.',
    ])


def get_post_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='➡️ СДЕЛАТЬ ОБМЕН', url='http://manager.tg.fexps.com/')],
            [
                InlineKeyboardButton(text='🤔 О НАС', url='http://about.tg.fexps.com/'),
                InlineKeyboardButton(text='💬 ОТЗЫВЫ', url='http://reviews.tg.fexps.com/'),
            ],
            [InlineKeyboardButton(text='💰 КАК ПРОХОДИТ ОБМЕН', url='http://deals.tg.fexps.com/')],
        ],
    )
    return keyboard


def image_draw_center(image_draw, coordinates, text):
    if not coordinates:
        return
    box_size = FONT_MONTSERRAT_SEMIBOLD.getbbox(text)
    text_coordinates = [
        coordinates[0][0] + (coordinates[1][0] - coordinates[0][0] - box_size[2]) / 2,
        coordinates[0][1] + (coordinates[1][1] - coordinates[0][1] - box_size[3]) / 2,
    ]
    text_coordinates[1] -= 7
    color = '#40403D'
    image_draw.text(
        text_coordinates,
        font=FONT_MONTSERRAT_SEMIBOLD,
        text=text,
        fill=color,
    )


async def get_pair_rate(
        commission_pack_value: CommissionPackValue,
        input_method: Method,
        output_method: Method,
) -> Optional[tuple]:
    rate_pair = await RatePairRepository().get_actual(
        commission_pack_value=commission_pack_value,
        input_method=input_method,
        output_method=output_method,
    )
    if not rate_pair:
        return
    rate_float = value_to_float(value=rate_pair.rate, decimal=rate_pair.rate_decimal)
    if f'{input_method.currency.id_str}{output_method.currency.id_str}' in ['usdusdt', 'usdtusd']:
        rate_float = (1 - rate_float) * 100
        if rate_float < 0:
            rate_float = -rate_float
        rate_float = round(rate_float)
        type_ = 'percent'
    else:
        if rate_float < 1:
            rate_float = 1 / rate_float
        type_ = 'value'
    return round(rate_float, 2), type_


async def post_create_fexps(commission_pack: CommissionPack) -> list[dict]:
    result = []
    for i_currency_id_str, o_currency_id_str in [
        ('rub', 'usd'), ('usd', 'rub'), ('usd', 'usdt'),
    ]:
        date_now = datetime.datetime.now(tz=datetime.timezone.utc)
        image_input_path = f'{settings.path_telegram}/source/fexps_{i_currency_id_str}{o_currency_id_str}.png'
        image_output_path = f'{settings.path_telegram}/images/fexps_{i_currency_id_str}{o_currency_id_str}.png'
        image = Image.open(image_input_path)
        image_draw = ImageDraw.Draw(image)
        commissions = []
        for commission_pack_value in await CommissionPackValueRepository().get_list(commission_pack=commission_pack):
            input_currency = await CurrencyRepository().get(id_str=i_currency_id_str)
            input_method = await MethodRepository().get(currency=input_currency, is_rate_default=True)
            if not input_method:
                continue
            output_currency = await CurrencyRepository().get(id_str=o_currency_id_str)
            output_method = await MethodRepository().get(currency=output_currency, is_rate_default=True)
            if not output_method:
                continue
            rate_raw = await get_pair_rate(
                commission_pack_value=commission_pack_value,
                input_method=input_method,
                output_method=output_method,
            )
            if not rate_raw:
                continue
            rate, type_ = rate_raw
            rate_str = f'{rate}'
            if type_ == 'percent':
                rate_str += '%'
            name = f'{commission_pack_value.value_from}-{commission_pack_value.value_to}'
            if commission_pack_value.value:
                commission_value = round(value_to_float(value=commission_pack_value.value), 2)
                commissions += [
                    f'{RANGES.get(name)} — {commission_value} USD',
                ]
            image_draw_center(
                image_draw=image_draw,
                coordinates=COORDINATES_RANGES.get(name),
                text=RANGES.get(name) + '*' if commission_pack_value.value else RANGES.get(name),
            )
            image_draw_center(
                image_draw=image_draw,
                coordinates=COORDINATES_RATES.get(name),
                text=rate_str,
            )
        if commissions:
            comissions_text = '* Дополнительная комиссия: '
            comissions_text += ', '.join(commissions) + '.'
            # Дополнительная комиссия
            image_draw.text(
                (228, 847),
                font=FONT_MONTSERRAT_REGULAR,
                text=comissions_text,
                fill='#333',
            )
        image_draw.text(
            (1210, 101),
            font=FONT_JETBRAINSMONO_REGULAR,
            text='{}'.format(date_now.strftime('%Y-%m-%d %H:%M UTC')),
            fill='#333',
        )
        image.save(image_output_path)
        result += [
            {
                'name': f'{i_currency_id_str}{o_currency_id_str}',
                'image': image_output_path,
            },
        ]
    result += [
        {
            'name': f'default',
            'text': get_post_text(),
            'reply_markup': get_post_keyboard(),
        },
    ]
    return result
