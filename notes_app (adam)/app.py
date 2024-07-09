from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

notes = []

@app.route('/add_note', methods=['POST'])
def add_note():
    note = request.json.get('note')
    notes.append(note)
    return jsonify({'status': 'success', 'note': note}), 201

@app.route('/delete_note', methods=['POST'])
def delete_note():
    note = request.json.get('note')
    notes.remove(note)
    return jsonify({'status': 'success', 'note': note}), 200

@app.route('/get_notes', methods=['GET'])
def get_notes():
    return jsonify({'notes': notes}), 200

if __name__ == '__main__':
    app.run(debug=True)
