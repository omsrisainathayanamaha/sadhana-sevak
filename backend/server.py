from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from query_processor import synthesize_answer

app = Flask(__name__, static_folder='static', template_folder='templates')


# API route
@app.route('/submit', methods=['POST'])
def synthesize():
    query = request.json.get('query', '')
    response = synthesize_answer(query)
    return jsonify({"response": response})

# Route for serving the frontend
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
