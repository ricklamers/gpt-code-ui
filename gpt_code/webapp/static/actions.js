(() => {

    function getApiData() {
        fetch('http://127.0.0.1:5000/api')
            .then(response => response.json())
            .then(data => {
                const outputElement = document.querySelector('.kernel-outputs');
                data.results.forEach(function(result) {
                    if(result.trim().length == 0) {
                        return
                    }
                    var paragraph = document.createElement("p");
                    var content = document.createTextNode(result);
                    paragraph.appendChild(content);
                    outputElement.appendChild(paragraph);
                });
            })
            .catch(error => console.error('Error fetching data:', error));
    }

    function postData() {
        const inputElement = document.querySelector('textarea.input');
        const message = inputElement.value;

        fetch('http://127.0.0.1:5000/api', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: message })
        })
            .then(response => response.json())
            .then(data => {
                setTimeout(getApiData(), 500);
            })
            .catch(error => console.error('Error:', error));
    }

    function generateCode() {
        const inputElement = document.querySelector('textarea.text-input');
        const prompt = inputElement.value;

        fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt: prompt })
        })
            .then(response => response.json())
            .then(data => {
                const outputElement = document.querySelector('.code-outputs');
                outputElement.textContent = data.code;

                // Set the value of the code input textarea to the generated code
                const codeInputElement = document.querySelector('textarea.input');
                codeInputElement.value = data.code;

                // Call postData function to submit the form
                postData();
            })
            .catch(error => console.error('Error:', error));
    }

    const sendButton = document.querySelector('button.send-code');
    sendButton.addEventListener('click', postData);

    const generateButton = document.querySelector('button.send');
    generateButton.addEventListener('click', generateCode);

    setInterval(getApiData, 1000);

    function uploadFile(e) {
        e.preventDefault();

        const fileInput = document.querySelector('#file-input');
        const file = fileInput.files[0];
        // Get a ref to the status div
        // #upload-form .upload-status
        const statusElement = document.querySelector('#upload-form .upload-status');
        statusElement.textContent = 'Uploading...';

        if (!file) {
            console.error('No file selected');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error:', data.error);
                } else {
                    statusElement.textContent = 'File successfully uploaded';
                }
            })
            .catch(error => console.error('Error:', error));
    }

    const uploadForm = document.querySelector('#upload-form');
    uploadForm.addEventListener('submit', uploadFile);
})();
