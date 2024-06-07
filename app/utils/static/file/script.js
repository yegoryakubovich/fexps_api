const fileInput = document.getElementById('file-input');
const fileButton = document.getElementById('file-button');
const imageContainer = document.getElementById('image-container');
const fileMaxCount = 10;

fileButton.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', () => {
    const files = fileInput.files;
    imageContainer.innerHTML = '';
    if (files.length > fileMaxCount){
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
