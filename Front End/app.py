import openai

# Set your OpenAI API key
openai.api_key = r''  # Replace with your real key

def ask_chatbot(user_question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_question}
            ],
            temperature=0.7
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Chatbot failed: {e}"

from flask import Flask, request, jsonify
from flask_cors import CORS
import pytesseract
from PIL import Image
from transformers import pipeline
import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import traceback

app = Flask(__name__)
CORS(app)

# Load a question-answering pipeline
try:
    qa_pipeline = pipeline("question-answering")
except Exception as e:
    print(f"Error loading question-answering pipeline: {e}")
    qa_pipeline = None

# File names
file_names = [
    r'C:\Users\ajeev\Downloads\hotpotqa_dataset\hotpot_train_v1.1.json'
]

# Load knowledge.txt
try:
    with open("knowledge.txt", "r", encoding="utf-8") as f:
        knowledge_text = f.read()
except FileNotFoundError:
    print("knowledge.txt not found.")
    knowledge_text = ""
except Exception as e:
    print(f"Error reading knowledge.txt: {e}")
    knowledge_text = ""

# Load and split HotpotQA context
passages = []

def load_passages(files):
    for file_path in files:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    if 'context' in item:
                        for title, paras in item['context']:
                            text = " ".join(paras)
                            if text:
                                passages.append(f"{title}: {text}")
        except Exception as e:
            print(f"Error loading HotpotQA data from {file_path}: {e}")
            traceback.print_exc()
            continue

load_passages(file_names)

# Prepare TF-IDF vectorizer
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = None  # initialize to none.

if passages:
    try:
        tfidf_matrix = vectorizer.fit_transform(passages)
    except Exception as e:
        print(f"Error during TF-IDF Vectorizer fitting: {e}")
        traceback.print_exc()

def get_relevant_context(question, top_k=3):
    if tfidf_matrix is None:
        return knowledge_text  # return knowledge.txt if no matrix exists.
    try:
        question_vec = vectorizer.transform([question])
        similarities = cosine_similarity(question_vec, tfidf_matrix).flatten()
        top_indices = similarities.argsort()[-top_k:][::-1]
        best_passages = [passages[i] for i in top_indices]
        return " ".join(best_passages) + " " + knowledge_text  # add knowledge.txt context.
    except Exception as e:
        print(f"Error getting relevant context: {e}")
        traceback.print_exc()
        return knowledge_text  # return only knowledge text if other errors occur.

@app.route('/ask', methods=['POST'])
def ask_question():
    if qa_pipeline is None:
        return jsonify({'error': 'Question-answering pipeline not loaded.'}), 500

    question = ""
    context = ""

    # Case 1: Text input via JSON
    if request.content_type.startswith('application/json'):
        data = request.get_json()
        question = data.get('question', '')
        context = get_relevant_context(question)

    # Case 2: Image input via multipart/form-data
    elif request.content_type.startswith('multipart/form-data'):
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        image_file = request.files['image']
        try:
            image = Image.open(image_file.stream)
            context = pytesseract.image_to_string(image)
            question = "What is the image about?"
        except Exception as e:
            return jsonify({'error': f'Error processing image: {str(e)}'}), 400

    else:
        return jsonify({'error': 'Unsupported content type'}), 400

    if not question.strip() or not context.strip():
        return jsonify({'error': 'Missing question or context'}), 400

    try:
        result = qa_pipeline(question=question, context=context)

        # Fallback if QA model gives generic/empty/weak answer
        answer = result['answer'].strip()
        if not answer or answer.lower() in ["unknown", "not sure", "i don't know", ""]:
            chatbot_answer = ask_chatbot(question)
            return jsonify({'answer': chatbot_answer, 'source': 'chatbot'})
        else:
            return jsonify({'answer': answer, 'source': 'qa_model'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)