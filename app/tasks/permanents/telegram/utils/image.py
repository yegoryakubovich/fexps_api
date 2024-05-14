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


from datetime import datetime, timezone

from PIL import Image, ImageDraw, ImageFont

from app.repositories import RatePairRepository, CurrencyRepository
from config import settings

COORDINATES_RATES = [
    [[1455, 280], [1792, 415]],
    [[1455, 435], [1792, 570]],
    [[1455, 590], [1792, 725]],
    [[1455, 745], [1792, 880]],
    [[1455, 900], [1792, 1035]],
]

FONT_MONTSERRAT_SEMIBOLD = ImageFont.truetype(f'{settings.path_telegram}/fonts/montserrat_semibold.ttf', 70)
FONT_MONTSERRAT_REGULAR = ImageFont.truetype(f'{settings.path_telegram}/fonts/montserrat_regular.ttf', 36)
FONT_JETBRAINSMONO_REGULAR = ImageFont.truetype(f'{settings.path_telegram}/fonts/jetbrainsmono_regular.ttf', 42)


def image_draw_center(image_draw, coordinates, text):
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
    pairs = []
    for currency_input_id_str, currency_output_id_str in settings.telegram_rate_pairs:
        pair = (currency_input_id_str, currency_output_id_str)
        currency_input = await CurrencyRepository().get_by_id_str(id_str=currency_input_id_str)
        currency_output = await CurrencyRepository().get_by_id_str(id_str=currency_output_id_str)
        i = len(pairs)
        rate_pair = await RatePairRepository().get(currency_input=currency_input, currency_output=currency_output)
        if not rate_pair:
            continue
        rate = rate_pair.value / 10 ** rate_pair.rate_decimal
        if rate < 1:
            rate = round(1 / rate, 2)
        image_draw_center(
            image_draw=image_draw,
            coordinates=COORDINATES_RATES[i],
            text=f'{rate}',
        )
        pairs.append(pair)
    image_draw.text(
        (1212, 116),
        font=FONT_JETBRAINSMONO_REGULAR,
        text='{}'.format(datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M (UTC)')),
        fill='#ffffff',
    )
    image.save(image_output_path)
    return image_output_path
