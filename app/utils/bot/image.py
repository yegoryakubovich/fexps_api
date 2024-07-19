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


import datetime
from typing import Optional

from PIL import Image, ImageDraw, ImageFont
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.db.models import Method, CommissionPack
from app.repositories import RatePairRepository, CurrencyRepository, MethodRepository
from app.utils.value import value_to_float
from config import settings

WEEK_DAY = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
MONTH_DAY = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня']
MONTH_DAY += ['июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']

COORDINATES_RATES = {
    'usdrub': [[1455, 280], [1792, 415]],
    'rubusd': [[1455, 435], [1792, 570]],
    'usdtusd': [[1455, 590], [1792, 725]],
    'usdusdt': [[1455, 745], [1792, 880]],
}
FONT_MONTSERRAT_SEMIBOLD = ImageFont.truetype(f'{settings.path_telegram}/fonts/montserrat_semibold.ttf', 70)
FONT_MONTSERRAT_REGULAR = ImageFont.truetype(f'{settings.path_telegram}/fonts/montserrat_regular.ttf', 36)
FONT_JETBRAINSMONO_REGULAR = ImageFont.truetype(f'{settings.path_telegram}/fonts/jetbrainsmono_regular.ttf', 42)


def get_post_text() -> str:
    date_now = datetime.datetime.now(tz=datetime.timezone.utc)
    return '\n'.join([
        f'🗓 Наступило {date_now.day} {MONTH_DAY[date_now.month - 1]}, {WEEK_DAY[date_now.weekday()]}.',
        f'',
        f'🤝 Прекрасная возможность обменять деньги по ВЫГОДНОМУ КУРСУ вместе с Sowa Pay.',
    ])


def get_post_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='➡️ СДЕЛАТЬ ОБМЕН', url=settings.telegram_manager)],
            [
                InlineKeyboardButton(text='🤔 О НАС', url=settings.telegram_about),
                InlineKeyboardButton(text='💬 ОТЗЫВЫ', url=settings.telegram_reviews),
            ],
            [InlineKeyboardButton(text='💰 КАК ПРОХОДИТ ОБМЕН', url=settings.telegram_info)],
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
    color = '#ffffff'
    image_draw.text(
        text_coordinates,
        font=FONT_MONTSERRAT_SEMIBOLD,
        text=text,
        fill=color,
    )


async def image_create(commission_pack: CommissionPack, ):
    date_now = datetime.datetime.now(tz=datetime.timezone.utc)
    image_input_path = f'{settings.path_telegram}/source/{commission_pack.filename}'
    image_output_path = f'{settings.path_telegram}/images/{commission_pack.filename}'
    image = Image.open(image_input_path)
    image_draw = ImageDraw.Draw(image)
    for input_currency_id_str, output_currency_id_str in settings.telegram_rate_pairs:
        input_currency = await CurrencyRepository().get(id_str=input_currency_id_str)
        input_method = await MethodRepository().get(currency=input_currency, is_rate_default=True)
        if not input_method:
            continue
        output_currency = await CurrencyRepository().get(id_str=output_currency_id_str)
        output_method = await MethodRepository().get(currency=output_currency, is_rate_default=True)
        if not output_method:
            continue
        rate_raw = await get_pair_rate(
            commission_pack=commission_pack,
            input_method=input_method,
            output_method=output_method,
        )
        if not rate_raw:
            continue
        rate, type_ = rate_raw
        rate_str = f'{rate}'
        if type_ == 'percent':
            rate_str += '%'
        image_draw_center(
            image_draw=image_draw,
            coordinates=COORDINATES_RATES.get(f'{input_currency.id_str}{output_currency.id_str}'),
            text=rate_str,
        )
    image_draw.text(
        (1245, 116),
        font=FONT_JETBRAINSMONO_REGULAR,
        text='{}'.format(date_now.strftime('%Y-%m-%d %H:%M (UTC)')),
        fill='#ffffff',
    )
    image.save(image_output_path)
    return image_output_path


async def get_pair_rate(
        commission_pack: CommissionPack,
        input_method: Method,
        output_method: Method,
) -> Optional[tuple]:
    rate_pair = await RatePairRepository().get_actual(
        commission_pack=commission_pack,
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
        type_ = 'percent'
    else:
        if rate_float < 1:
            rate_float = 1 / rate_float
        type_ = 'value'
    return round(rate_float, 2), type_
