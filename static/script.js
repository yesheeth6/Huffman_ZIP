document.getElementById('uploadBtn').addEventListener('click', function () {
    const form = document.getElementById('uploadForm');
    const formData = new FormData(form);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = `
            <p>${data.message}</p>
            <p>Download encoded file: <a href="${data.encoded_file}" download>encoded.txt</a></p>
            <textarea readonly>${JSON.stringify(data.huffman_codes, null, 2)}</textarea>
        `;
    })
    .catch(error => console.error('Error:', error));
});
resultDiv.innerHTML = `
    <p>${data.message}</p>
    <p>Download encoded file: <a href="${data.encoded_file}" download>encoded.txt</a></p>
    <textarea readonly>${JSON.stringify(data.huffman_codes, null, 2)}</textarea>
`;
