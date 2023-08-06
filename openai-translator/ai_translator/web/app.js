var MAX_FILE_SIZE_MB = 10;  // Set the maximum file size in MB

document.getElementById('file-upload').addEventListener('change', function() {
    // Enable the submit button and language selects when a file is selected
    var fileInput = document.getElementById('file-upload');
    var file = fileInput.files[0];
    if (file.size / 1024 / 1024 > MAX_FILE_SIZE_MB) {
        alert('File is too large! Please select a file smaller than ' + MAX_FILE_SIZE_MB + 'MB.');
        fileInput.value = '';  // Clear the input
        return;
    }

    document.getElementById('src-lang').disabled = false;
    document.getElementById('dst-lang').disabled = false;
    document.getElementById('submit-button').disabled = false;
});

document.getElementById('submit-button').addEventListener('click', function() {
    var fileInput = document.getElementById('file-upload');
    var file = fileInput.files[0];
    var formData = new FormData();
    formData.append('file', file);
    formData.append('src_lang', document.getElementById('src-lang').value);
    formData.append('dst_lang', document.getElementById('dst-lang').value);

    var request = new XMLHttpRequest();
    request.open('POST', 'http://localhost:8080/translate', true);
    request.upload.onprogress = function(e) {
        if (e.lengthComputable) {
            var percentage = (e.loaded / e.total) * 100;
            document.querySelector('.progress-bar div').style.width = percentage + '%';
        }
    };
    request.onloadend = function(e) {
        var blob = request.response;
        // Create a URL for the blob
        var url = window.URL.createObjectURL(blob);
        var downloadLink = document.getElementById('download-link');
        downloadLink.href = url;
        downloadLink.style.display = 'block';  // Make the download link visible
    };
    request.onerror = function() {
        console.log('Fetch failed: ', request.status);
    };
    request.responseType = 'blob';
    request.send(formData);
});
