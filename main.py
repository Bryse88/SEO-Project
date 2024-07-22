
# Note: changes were only made to app.js and notes.html, more info can be found there.

import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, session, request, render_template, flash, jsonify
from flask_oauthlib.client import OAuth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from forms import RegistrationForm
from flask_behind_proxy import FlaskBehindProxy
from flask_bootstrap import Bootstrap
from flask_cors import CORS
import secrets

load_dotenv()
app = Flask(__name__)
CORS(app)
bootstrap = Bootstrap(app)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = secrets.token_hex(16)
oauth = OAuth(app)

# In-memory notes storage for simplicity
notes_storage = []

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


@app.route('/add_note', methods=['POST'])
def add_note():
    note = request.json.get('note')
    if note:
        notes_storage.append(note)
        return jsonify({'status': 'success', 'note': note}), 201
    return jsonify({'status': 'failure', 'message': 'Note is required'}), 400

@app.route('/delete_note', methods=['POST'])
def delete_note():
    note = request.json.get('note')
    if note in notes_storage:
        notes_storage.remove(note)
        return jsonify({'status': 'success', 'note': note}), 200
    return jsonify({'status': 'failure', 'message': 'Note not found'}), 400

@app.route('/get_notes', methods=['GET'])
def get_notes():
    return jsonify({'notes': notes_storage}), 200

@app.route('/')
def index():
    form = RegistrationForm()
    return render_template('main.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/notes')
def notes():
    return render_template('notes.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
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
def create_event_form():
    return render_template('notes.html')

@app.route('/create_event', methods=['POST'])
def create_event():
    description = request.form['description']
    summary = request.form['summary']
    publish_to_calendar = 'publishToCalendar' in request.form
    # Save the note
    flash(f'Note added: {description}', 'success')
    if publish_to_calendar:
        start = request.form['start']
        end = request.form['end']
        # Ensure start and end times are not empty
        if not start or not end:
            flash('Start and End date and time must be provided.', 'error')
            return redirect(url_for('notes'))
        # Ensure dateTime includes seconds
        start = start + ":00"
        end = end + ":00"
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
        try:
            credentials = Credentials(session['google_token'][0])
            service = build('calendar', 'v3', credentials=credentials)
            print("Creating event with payload:", event)  # Debugging
            created_event = service.events().insert(calendarId='primary', body=event).execute()
            # Print the response to debug
            print("Created Event: ", created_event)
            flash(f'Event created: {created_event.get("htmlLink")}', 'success')
        except Exception as e:
            print("An error occurred:", e)  # Debugging
            flash(f'An error occurred: {e}', 'error')
            return redirect(url_for('notes'))
    return redirect(url_for('notes'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
