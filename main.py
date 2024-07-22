import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, session, request, render_template, flash
from flask_oauthlib.client import OAuth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import openai
from forms import RegistrationForm
from flask_behind_proxy import FlaskBehindProxy
from flask_bootstrap import Bootstrap
import secrets

load_dotenv()
app = Flask(__name__)
bootstrap = Bootstrap(app)
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

openai.api_key = os.getenv("OPENAI_API_KEY")

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
    return redirect(url_for('notes'))

@app.route('/create_event', methods=['POST'])
def create_event():
    description = request.form['description']
    summary = request.form['summary']
    category = request.form['category']
    publish_to_calendar = 'publishToCalendar' in request.form
    use_ai_suggestion = 'useAiSuggestion' in request.form

    if publish_to_calendar:
        start = request.form['start']
        end = request.form['end']
        if not start or not end:
            flash('Start and End date and time must be provided.', 'error')
            return redirect(url_for('notes'))

        if use_ai_suggestion:
            try:
                credentials = Credentials(session['google_token'][0])
                service = build('calendar', 'v3', credentials=credentials)
                events_result = service.events().list(calendarId='primary', maxResults=10, singleEvents=True,
                                                      orderBy='startTime').execute()
                events = events_result.get('items', [])

                openai_response = get_openai_suggestion(events, summary, category)
                suggested_time = openai_response.get('suggested_time')
                start, end = suggested_time['start'], suggested_time['end']
                flash(f'Suggested time by AI: Start: {start}, End: {end}', 'info')

            except Exception as e:
                flash(f'An error occurred while fetching AI suggestion: {e}', 'error')
                return redirect(url_for('notes'))

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
            },
            'extendedProperties': {
                'private': {
                    'category': category
                }
            }
        }
        try:
            credentials = Credentials(session['google_token'][0])
            service = build('calendar', 'v3', credentials=credentials)
            print("Creating event with payload:", event)
            created_event = service.events().insert(calendarId='primary', body=event).execute()
            print("Created Event: ", created_event)
            flash(f'Event created: {created_event.get("htmlLink")}', 'success')
        except Exception as e:
            print("An error occurred:", e)
            flash(f'An error occurred: {e}', 'error')
            return redirect(url_for('notes'))

    return redirect(url_for('notes'))

def get_openai_suggestion(events, summary, category):
    events_summary = "\n".join([f"{event['start']['dateTime']} to {event['end']['dateTime']}: {event['summary']}" for event in events])
    prompt = f"""
    You are an intelligent assistant. Here are the existing events in the user's calendar:
    {events_summary}

    The user wants to add a new event with the following details:
    Summary: {summary}
    Category: {category}

    Please suggest the optimal start and end time for this new event based on the user's current schedule and the category of the event.
    """
    
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=150
    )
    
    suggested_time_text = response.choices[0].text.strip()
    suggested_time = parse_suggested_time(suggested_time_text)
    return {'suggested_time': suggested_time}

def parse_suggested_time(text):
    # A simple parser to extract start and end time from OpenAI's response
    lines = text.split("\n")
    start = lines[0].split("Start: ")[1].strip()
    end = lines[1].split("End: ")[1].strip()
    return {'start': start, 'end': end}

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5050)
