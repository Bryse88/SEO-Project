from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from forms import RegistrationForm
from flask_behind_proxy import FlaskBehindProxy
from flask_bootstrap import Bootstrap4
import secrets
from flask_cors import CORS

app = Flask(__name__)
bootstrap = Bootstrap4(app)
proxied = FlaskBehindProxy(app)
CORS(app)

app.config['SECRET_KEY'] = secrets.token_hex(16)

# List to store notes
notes = []

# Home page with login and register links
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('main.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Register page with form
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

# Endpoint to add a note
@app.route('/add_note', methods=['POST'])
def add_note():
    note = request.json.get('note')
    notes.append(note)
    return jsonify({'status': 'success', 'note': note}), 201

# Endpoint to delete a note
@app.route('/delete_note', methods=['POST'])
def delete_note():
    note = request.json.get('note')
    notes.remove(note)
    return jsonify({'status': 'success', 'note': note}), 200

# Endpoint to get all notes
@app.route('/get_notes', methods=['GET'])
def get_notes():
    return jsonify({'notes': notes}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
