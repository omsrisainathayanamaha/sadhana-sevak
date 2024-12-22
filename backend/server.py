from flask import Flask, request, jsonify
from query_processor import synthesize_answer

app = Flask(__name__)

@app.route('/api/synthesize', methods=['POST'])
def synthesize():
    query = request.json['query']
    response = synthesize_answer(query)
    return jsonify({"response": response})