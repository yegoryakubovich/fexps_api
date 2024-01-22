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


from starlette.datastructures import Headers


class Device:
    platform: str
    is_phone: bool
    versions: dict

    def __init__(self, headers: Headers):
        header_platform = headers.get('sec-ch-ua-platform')
        header_is_phone = headers.get('sec-ch-ua-mobile')
        header_versions = headers.get('sec-ch-ua')

        if header_platform:
            self.platform = header_platform.replace('"', '')
        if header_is_phone:
            self.header_is_phone = True if header_platform.replace('?', '') == '1' else False
        if header_versions:
            self.versions = {}
            for nv in header_versions.split(', '):
                name, version = nv.split(';v=')
                name = name.replace('"', '')
                version = version.replace('"', '')
                self.versions[name] = version
