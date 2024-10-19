function convertToMp3() {
    const url = document.getElementById('video-url').value;
    const statusElement = document.getElementById('status');
    const loadingElement = document.getElementById('loading'); // Assuming there's a loading indicator element
    
    // Basic URL validation
    const urlPattern = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$/;
    if (!url || !urlPattern.test(url)) {
        statusElement.innerHTML = 'Please enter a valid YouTube video URL.';
        return;
    }

    // Show loading indicator and status message
    loadingElement.style.display = 'block';
    statusElement.innerHTML = 'Converting... please wait.';

    fetch('/convert', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
        loadingElement.style.display = 'none'; // Hide loading indicator
        if (data.success) {
            statusElement.innerHTML = `Conversion successful! <a href="/downloads/${data.file}" download>Download MP3</a>`;
        } else {
            statusElement.innerHTML = 'Conversion failed. Please try again.';
        }
    })
    .catch(error => {
        loadingElement.style.display = 'none'; // Hide loading indicator
        console.error('Error:', error);
        statusElement.innerHTML = 'An error occurred. Please check your connection or try again later.';
    });
}
