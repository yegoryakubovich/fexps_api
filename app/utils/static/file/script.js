//
// (c) 2024, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//

const fileInput = document.getElementById('file-input');
const fileButton = document.getElementById('file-button');
const continueButton = document.getElementById('continue-button')
const imageContainer = document.getElementById('image-container');
const fileMaxCount = 10;

fileButton.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', () => {
    const files = fileInput.files;
    imageContainer.innerHTML = '';
    if (files.length > fileMaxCount) {
        alert('max files / макс. файлов ' + fileMaxCount);
        return
    }
    for (const file of files) {
        const imgWrapper = document.createElement('div');
        imgWrapper.className = 'image-wrapper';
        const img = document.createElement('img');
        const filename_split = file.name.split('.')
        if (['jpg', 'png'].includes(filename_split[filename_split.length - 1])) {
            const reader = new FileReader();
            reader.onload = (e) => {
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        } else {
            img.src = 'https://74foto.ru/800/600/http/mpsatp.ru/wp-content/uploads/2021/01/Untitled-2-01-768x769.png';
        }
        imgWrapper.appendChild(img);
        imageContainer.appendChild(imgWrapper);
    }
});

continueButton.addEventListener('click', () => {
    window.history.back();
});