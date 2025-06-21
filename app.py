import os
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from collections import Counter
import heapq
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(frequency):
    heap = [Node(char, freq) for char, freq in frequency.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    return heap[0]

def assign_codes(node, current_code, codes):
    if not node:
        return
    if node.char is not None:
        codes[node.char] = current_code
    assign_codes(node.left, current_code + "0", codes)
    assign_codes(node.right, current_code + "1", codes)

def decode_text(encoded_text, huffman_codes):
    reverse_codes = {v: k for k, v in huffman_codes.items()}
    current_code = ""
    decoded_text = ""

    for bit in encoded_text:
        current_code += bit
        if current_code in reverse_codes:
            decoded_text += reverse_codes[current_code]
            current_code = ""

    return decoded_text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    with open(filepath, 'r', encoding='utf-8') as f:
        input_text = f.read()

    frequency = Counter(input_text)
    huffman_tree = build_huffman_tree(frequency)
    huffman_codes = {}
    assign_codes(huffman_tree, "", huffman_codes)

    encoded_text = ''.join(huffman_codes[char] for char in input_text)
    combined_data = {
        "huffman_codes": huffman_codes,
        "encoded_text": encoded_text
    }

    encoded_filename = f"{os.path.splitext(filename)[0]}_encoded.txt"
    encoded_filepath = os.path.join(app.config['UPLOAD_FOLDER'], encoded_filename)
    with open(encoded_filepath, 'w', encoding='utf-8') as f:
        f.write(json.dumps(combined_data))

    return jsonify({
        "message": "File encoded successfully",
        "encoded_file": f"/uploads/{encoded_filename}"
    })

@app.route('/decode', methods=['POST'])
def decode_file():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    huffman_codes = data['huffman_codes']
    encoded_text = data['encoded_text']
    decoded_text = decode_text(encoded_text, huffman_codes)

    decoded_filename = f"{os.path.splitext(filename)[0]}_decoded.txt"
    decoded_filepath = os.path.join(app.config['UPLOAD_FOLDER'], decoded_filename)
    with open(decoded_filepath, 'w', encoding='utf-8') as f:
        f.write(decoded_text)

    return jsonify({
        "message": "File decoded successfully",
        "decoded_file": f"/uploads/{decoded_filename}"
    })

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
