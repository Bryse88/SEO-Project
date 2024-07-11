import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, session, request, render_template, flash, jsonify
from flask_oauthlib.client import OAuth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from forms import RegistrationForm
from flask_behind_proxy import FlaskBehindProxy
from flask_bootstrap import Bootstrap4
from functools import wraps
import secrets

load_dotenv()

app = Flask(__name__)
bootstrap = Bootstrap4(app)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = secrets.token_hex(16)

oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=os.getenv('GOOGLE_CLIENT_ID'),
    consumer_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/calendar',
        'prompt': 'consent'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

notes = []

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'google_token' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    form = RegistrationForm()
    return render_template('main.html')

@app.route('/about')
@login_required
def about(): 
    return render_template('about.html')

@app.route('/notes')
@login_required
def notes_page():
    return render_template('notes.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if not form.email.data.endswith('@gmail.com'):
            flash('Registration failed: Only @gmail.com accounts are allowed.', 'danger')
        else:
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))

@app.route('/oauth2callback')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )

    session['google_token'] = (response['access_token'], '')
    return redirect(url_for('create_event_form'))

@app.route('/create_event_form')
@login_required
def create_event_form():
    return render_template('calendar.html')

@app.route('/create_event', methods=['POST'])
@login_required
def create_event():
    description = request.form['description']
    publish_to_calendar = 'publishToCalendar' in request.form

    # Save the note
    # You can add code here to save the note to your preferred storage (database, file, etc.)
    flash(f'Note added: {description}', 'success')

    if publish_to_calendar:
        summary = request.form['summary']
        start = request.form['start']
        end = request.form['end']

        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start,
                'timeZone': 'America/Chicago'
            },
            'end': {
                'dateTime': end,
                'timeZone': 'America/Chicago'
            }
        }

        credentials = Credentials(session['google_token'][0])
        service = build('calendar', 'v3', credentials=credentials)
        event = service.events().insert(calendarId='primary', body=event).execute()

        flash(f'Event created: {event.get("htmlLink")}', 'success')

    return redirect(url_for('notes'))

@app.route('/add_note', methods=['POST'])
@login_required
def add_note():
    note = request.json.get('note')
    notes.append(note)
    return jsonify({'status': 'success', 'note': note}), 201

@app.route('/delete_note', methods=['POST'])
@login_required
def delete_note():
    note = request.json.get('note')
    if note in notes:
        notes.remove(note)
        return jsonify({'status': 'success', 'note': note}), 200
    return jsonify({'status': 'error', 'message': 'Note not found'}), 404

@app.route('/get_notes', methods=['GET'])
@login_required
def get_notes():
    return jsonify({'notes': notes}), 200

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5050)
