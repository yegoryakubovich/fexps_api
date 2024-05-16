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
import logging
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from app.db.models import Currency, RatePair
from app.repositories import RatePairRepository, CurrencyRepository
from config import settings

COORDINATES_RATES = {
    'usdrub': [[1455, 280], [1792, 415]],
    'rubusd': [[1455, 435], [1792, 570]],
    'usdtusd': [[1455, 590], [1792, 725]],
    'usdusdt': [[1455, 745], [1792, 880]],
}

FONT_MONTSERRAT_SEMIBOLD = ImageFont.truetype(f'{settings.path_telegram}/fonts/montserrat_semibold.ttf', 70)
FONT_MONTSERRAT_REGULAR = ImageFont.truetype(f'{settings.path_telegram}/fonts/montserrat_regular.ttf', 36)
FONT_JETBRAINSMONO_REGULAR = ImageFont.truetype(f'{settings.path_telegram}/fonts/jetbrainsmono_regular.ttf', 42)


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


async def image_create():
    image_input_path = f'{settings.path_telegram}/source/sowapay.png'
    image_output_path = f'{settings.path_telegram}/images/sowapay.png'
    image = Image.open(image_input_path)
    image_draw = ImageDraw.Draw(image)
    for currency_input_id_str, currency_output_id_str in settings.telegram_rate_pairs:
        currency_input = await CurrencyRepository().get_by_id_str(id_str=currency_input_id_str)
        currency_output = await CurrencyRepository().get_by_id_str(id_str=currency_output_id_str)
        rate_raw = await get_pair_rate(currency_input=currency_input, currency_output=currency_output)
        if not rate_raw:
            continue
        rate, type_ = rate_raw
        rate_str = f'{rate}'
        if type_ == 'percent':
            rate_str += '%'
        image_draw_center(
            image_draw=image_draw,
            coordinates=COORDINATES_RATES.get(f'{currency_input.id_str}{currency_output.id_str}'),
            text=rate_str,
        )
    image_draw.text(
        (1245, 116),
        font=FONT_JETBRAINSMONO_REGULAR,
        text='{}'.format(datetime.datetime.now(tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M (UTC)')),
        fill='#ffffff',
    )
    image.save(image_output_path)
    return image_output_path


async def get_pair_rate(currency_input: Currency, currency_output: Currency) -> Optional[tuple]:
    rate_pair = await RatePairRepository().get(currency_input=currency_input, currency_output=currency_output)
    if not rate_pair or not await check_rate_actual(rate_pair=rate_pair):
        return
    rate = rate_pair.value / 10 ** rate_pair.rate_decimal
    if f'{currency_input.id_str}{currency_output.id_str}' in ['usdusdt', 'usdtusd']:
        rate = (1 - rate) * 100
        if rate < 0:
            rate = -rate
        type_ = 'percent'
    else:
        if rate < 1:
            rate = 1 / rate
        type_ = 'value'
    return round(rate, 2), type_


async def check_rate_actual(rate_pair: RatePair) -> bool:
    rate_date = rate_pair.created_at.replace(tzinfo=datetime.timezone.utc)
    date_now = datetime.datetime.now(tz=datetime.timezone.utc)
    date_delta = datetime.timedelta(minutes=settings.rate_actual_minutes)
    date_check = date_now - date_delta
    if rate_date < date_check:
        return False
    return True
