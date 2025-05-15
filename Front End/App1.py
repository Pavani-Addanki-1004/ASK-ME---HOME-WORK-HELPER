from flask import Flask, request, jsonify
from flask_cors import CORS
import pytesseract
from PIL import Image
from transformers import pipeline

app = Flask(__name__)
CORS(app)

# Load a question-answering pipeline
qa_pipeline = pipeline("question-answering")

# Load context from a local knowledge file
with open("knowledge.txt", "r", encoding="utf-8") as f:
    full_context = f.read()

@app.route('/ask', methods=['POST'])
def ask_question():
    question = ""
    context = ""

    # Case 1: Text input via JSON
    if request.content_type.startswith('application/json'):
        data = request.get_json()
        question = data.get('question', '')
        context = full_context  # use the whole knowledge base
    
    # Case 2: Image input via multipart/form-data
    elif request.content_type.startswith('multipart/form-data'):
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        image_file = request.files['image']
        image = Image.open(image_file.stream)
        context = pytesseract.image_to_string(image)
        question = "What is the image about?"  # Can be improved later
    
    else:
        return jsonify({'error': 'Unsupported content type'}), 400

    if not question.strip() or not context.strip():
        return jsonify({'error': 'Missing question or context'}), 400

    try:
        result = qa_pipeline(question=question, context=context)
        return jsonify({'answer': result['answer']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
