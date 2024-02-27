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


from os import path, remove

from fastapi import UploadFile
from PIL import Image as ImagePillow

from app.services.meal_report_image import MealReportImageService
from app.utils.exceptions import InvalidFileType, TooLargeFile, ModelDoesNotExist
from config import settings
from app.services.base import BaseService
from app.db.models import Image, Session
from app.repositories import ImageRepository, MealReportRepository
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required


class ImageService(BaseService):

    image_services = {
        'meal_report': MealReportImageService(),
    }

    model_repositories = {
        'meal_report': MealReportRepository(),
    }

    async def _create(
            self,
            session: Session,
            file: UploadFile,
            model: str,
            model_id: int | str,
            by_admin: bool = False,
    ) -> Image:
        id_str = await create_id_str()

        await self.check_file(file=file)

        try:
            service = self.image_services[model]
        except KeyError:
            raise ModelDoesNotExist(
                kwargs={
                    'model': 'model',
                    'id_type': 'name',
                    'id_value': model,
                },
            )

        if model_id.isnumeric():
            await self.model_repositories[model].get_by_id(id_=model_id)
        else:
            await self.model_repositories[model].get_by_id_str(id_str=model_id)

        action_parameters = {
            'creator': f'session_{session.id}',
            'id_str': id_str,
        }

        if by_admin:
            action_parameters.update(
                {
                    'by_admin': True,
                }
            )

        with open(f'{settings.path_images}/{id_str}.jpg', mode='wb') as image:
            file_content = await file.read()
            image.write(file_content)
            image.close()

        while path.getsize(f'{settings.path_images}/{id_str}.jpg') > 2097152:
            image = ImagePillow.open(f'{settings.path_images}/{id_str}.jpg')

            width, height = image.size
            new_size = (int(width // 1.5), int(height // 1.5))
            resized_image = image.resize(new_size)

            resized_image.save(f'{settings.path_images}/{id_str}.jpg', optimize=True, quality=90)

        image = await ImageRepository().create(
            id_str=id_str,
            model=model,
            model_id=model_id,
        )

        if by_admin:
            await service.create_by_admin(
                session=session,
                model_id=model_id,
                image_id_str=id_str,
            )
        else:
            await service.create(
                session=session,
                model_id=model_id,
                image_id_str=id_str,
            )

        await self.create_action(
            model=image,
            action='create',
            parameters=action_parameters
        )

        return image

    @session_required()
    async def create(
            self,
            session: Session,
            file: UploadFile,
            model: str,
            model_id: int | str,
            return_model: bool = False,
    ):
        image = await self._create(
            file=file,
            session=session,
            model=model,
            model_id=model_id
        )

        if return_model:
            return image

        return {'id_str': image.id_str}

    @session_required(permissions=['images'])
    async def create_by_admin(
            self,
            session: Session,
            file: UploadFile,
            model: str,
            model_id: int | str,
            return_model: bool = False,
    ):
        image = await self._create(
            file=file,
            session=session,
            model=model,
            model_id=model_id,
            by_admin=True
        )

        if return_model:
            return image

        return {'id_str': image.id_str}

    async def _delete(
            self,
            session: Session,
            id_str: str,
            by_admin: bool = False,
    ):
        image: Image = await ImageRepository().get_by_id_str(id_str=id_str)

        image_model_id = await self._get_model_image_id(model_name=image.model, model_id=image.model_id, image=image)

        action_parameters = {
            'deleter': f'session_{session.id}',
            'id_str': id_str,
        }

        if by_admin:
            action_parameters.update(
                {
                    'by_admin': True,
                }
            )

        service = self.image_services[image.model]
        if by_admin:
            await service.delete_by_admin(
                session=session,
                id_=image_model_id,
            )
        else:
            await service.delete(
                session=session,
                id_=image_model_id,
            )

        await ImageRepository().delete(model=image)

        remove(f'{settings.path_images}/{id_str}.jpg')

        await self.create_action(
            model=image,
            action='delete',
            parameters=action_parameters,
        )

        return {}

    @session_required()
    async def delete(
            self,
            session: Session,
            id_str: str,
    ):
        return await self._delete(
            session=session,
            id_str=id_str,
        )

    @session_required(permissions=['images'])
    async def delete_by_admin(
            self,
            session: Session,
            id_str: str,
    ):
        return await self._delete(
            session=session,
            id_str=id_str,
            by_admin=True,
        )

    @staticmethod
    async def check_file(file: UploadFile):
        if 'image' not in file.content_type:
            raise InvalidFileType()
        if file.size >= 16777216:
            raise TooLargeFile()

    async def _get_model_image_id(
            self,
            model_name: str,
            model_id: int | str,
            image: Image,
    ):
        image_service = self.image_services[model_name]
        model_image = await image_service.get_by_id_and_image(id_=model_id, image=image)
        return model_image.id

