
import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, session, request, render_template, flash
from flask_oauthlib.client import OAuth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from forms import RegistrationForm
from flask_behind_proxy import FlaskBehindProxy
from flask_bootstrap import Bootstrap4
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
        return redirect(url_for('main.html'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('main.html'))

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
    return render_template('calendar.html')

@app.route('/create_event', methods=['POST'])
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


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5050 )