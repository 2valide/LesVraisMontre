document.addEventListener('DOMContentLoaded', function () {
    const dropArea = document.getElementById('dropArea');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.getElementById('browseBtn');
    const imagePreview = document.getElementById('imagePreview');
    const fileInfo = document.getElementById('fileInfo');
    const submitBtn = document.getElementById('submitBtn');

    browseBtn.addEventListener('click', function () {
        fileInput.click();
    });

    dropArea.addEventListener('click', function (e) {
        if (e.target === dropArea) {
            fileInput.click();
        }
    });

    setupDragAndDrop();

    fileInput.addEventListener('change', updateFileInfo);

    function setupDragAndDrop() {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });

        dropArea.addEventListener('drop', handleDrop, false);
    }

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight() {
        dropArea.classList.add('highlight');
    }

    function unhighlight() {
        dropArea.classList.remove('highlight');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length) {
            fileInput.files = files;
            updateFileInfo();
        }
    }

    function updateFileInfo() {
        const file = fileInput.files[0];
        if (file) {
            fileInfo.textContent = `${file.name} (${formatFileSize(file.size)})`;

            const reader = new FileReader();
            reader.onload = function (e) {
                imagePreview.src = e.target.result;
                imagePreview.style.display = 'inline-block';
                submitBtn.style.display = 'inline-block';
            };
            reader.readAsDataURL(file);
        }
    }

    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' octets';
        else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' Ko';
        else return (bytes / 1048576).toFixed(1) + ' Mo';
    }
});