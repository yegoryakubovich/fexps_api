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


from enum import Enum
from typing import Any, Optional, List, Union, Sequence, Dict, Type, Callable

from fastapi import APIRouter, params
from fastapi.datastructures import Default
from fastapi.routing import APIRoute
from fastapi.types import IncEx, DecoratedCallable
from fastapi.utils import generate_unique_id
from starlette.responses import Response, JSONResponse
from starlette.routing import BaseRoute


class Router(APIRouter):
    def __init__(
            self,
            routes_included=None,
            **kwargs,
    ):
        super().__init__(**kwargs)
        if routes_included is None:
            routes_included = []

        for r in routes_included:
            self.include_router(r)

    def get(
            self,
            path: str = '',
            *,
            response_model: Any = Default(None),
            status_code: Optional[int] = None,
            tags: Optional[List[Union[str, Enum]]] = None,
            dependencies: Optional[Sequence[params.Depends]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            response_description: str = "Successful Response",
            responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
            deprecated: Optional[bool] = None,
            operation_id: Optional[str] = None,
            response_model_include: Optional[IncEx] = None,
            response_model_exclude: Optional[IncEx] = None,
            response_model_by_alias: bool = True,
            response_model_exclude_unset: bool = False,
            response_model_exclude_defaults: bool = False,
            response_model_exclude_none: bool = False,
            include_in_schema: bool = True,
            response_class: Type[Response] = Default(JSONResponse),
            name: Optional[str] = None,
            callbacks: Optional[List[BaseRoute]] = None,
            openapi_extra: Optional[Dict[str, Any]] = None,
            generate_unique_id_function: Callable[[APIRoute], str] = Default(
                generate_unique_id
            ),
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        if not dependencies:
            dependencies = []
        return self.api_route(
            path=path,
            response_model=response_model,
            status_code=status_code,
            tags=tags,
            dependencies=dependencies,
            summary=summary,
            description=description,
            response_description=response_description,
            responses=responses,
            deprecated=deprecated,
            methods=["GET"],
            operation_id=operation_id,
            response_model_include=response_model_include,
            response_model_exclude=response_model_exclude,
            response_model_by_alias=response_model_by_alias,
            response_model_exclude_unset=response_model_exclude_unset,
            response_model_exclude_defaults=response_model_exclude_defaults,
            response_model_exclude_none=response_model_exclude_none,
            include_in_schema=include_in_schema,
            response_class=response_class,
            name=name,
            callbacks=callbacks,
            openapi_extra=openapi_extra,
            generate_unique_id_function=generate_unique_id_function,
        )

    def post(
            self,
            path: str = '',
            *,
            response_model: Any = Default(None),
            status_code: Optional[int] = None,
            tags: Optional[List[Union[str, Enum]]] = None,
            dependencies: Optional[Sequence[params.Depends]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            response_description: str = "Successful Response",
            responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
            deprecated: Optional[bool] = None,
            operation_id: Optional[str] = None,
            response_model_include: Optional[IncEx] = None,
            response_model_exclude: Optional[IncEx] = None,
            response_model_by_alias: bool = True,
            response_model_exclude_unset: bool = False,
            response_model_exclude_defaults: bool = False,
            response_model_exclude_none: bool = False,
            include_in_schema: bool = True,
            response_class: Type[Response] = Default(JSONResponse),
            name: Optional[str] = None,
            callbacks: Optional[List[BaseRoute]] = None,
            openapi_extra: Optional[Dict[str, Any]] = None,
            generate_unique_id_function: Callable[[APIRoute], str] = Default(
                generate_unique_id
            ),
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        if not dependencies:
            dependencies = []
        return self.api_route(
            path=path,
            response_model=response_model,
            status_code=status_code,
            tags=tags,
            dependencies=dependencies,
            summary=summary,
            description=description,
            response_description=response_description,
            responses=responses,
            deprecated=deprecated,
            methods=["POST"],
            operation_id=operation_id,
            response_model_include=response_model_include,
            response_model_exclude=response_model_exclude,
            response_model_by_alias=response_model_by_alias,
            response_model_exclude_unset=response_model_exclude_unset,
            response_model_exclude_defaults=response_model_exclude_defaults,
            response_model_exclude_none=response_model_exclude_none,
            include_in_schema=include_in_schema,
            response_class=response_class,
            name=name,
            callbacks=callbacks,
            openapi_extra=openapi_extra,
            generate_unique_id_function=generate_unique_id_function,
        )
