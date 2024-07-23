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
import logging

load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

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

# Retrieve the API key from the environment variable
my_api_key = os.getenv('OPENAI_API_KEY')

CATEGORY_COLORS = {
    'class': '1',  # Light blue
    'study': '2',  # Light green
    'meeting': '3',  # Purple
    'project': '4',  # Red
    'break': '5',  # Yellow
    'personal': '6',  # Orange
}

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
        start_date = request.form['start']
        end_date = request.form['end']
        start_time = request.form.get('startTime')
        end_time = request.form.get('endTime')

        if not start_date or not end_date:
            flash('Start and End dates must be provided.', 'error')
            return redirect(url_for('notes'))

        if use_ai_suggestion:
            try:
                credentials = Credentials(session['google_token'][0])
                service = build('calendar', 'v3', credentials=credentials)
                events_result = service.events().list(calendarId='primary', maxResults=10, singleEvents=True,
                                                      orderBy='startTime').execute()
                events = events_result.get('items', [])

                openai_response = generate_chat_response(events, summary, category, start_date, end_date)
                suggested_time = parse_suggested_time(openai_response)
                start_time, end_time = suggested_time['startTime'], suggested_time['endTime']
                flash(f'Suggested time by AI: Start: {start_time}, End: {end_time}', 'info')

            except Exception as e:
                logging.error(f"Error fetching AI suggestion: {e}")
                flash(f'An error occurred while fetching AI suggestion: {e}', 'error')
                return redirect(url_for('notes'))

        start = f"{start_date}T{start_time}:00"
        end = f"{end_date}T{end_time}:00"
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
            'colorId': CATEGORY_COLORS.get(category, '1')  # Default to '1' if category is not found
        }
        try:
            credentials = Credentials(session['google_token'][0])
            service = build('calendar', 'v3', credentials=credentials)
            logging.debug(f"Creating event with payload: {event}")
            created_event = service.events().insert(calendarId='primary', body=event).execute()
            logging.debug(f"Created Event: {created_event}")
            flash(f'Event created: {created_event.get("htmlLink")}', 'success')
        except Exception as e:
            logging.error(f"Error creating event: {e}")
            flash(f'An error occurred: {e}', 'error')
            return redirect(url_for('notes'))

    return redirect(url_for('notes'))

def generate_chat_response(events, summary, category, start_date, end_date):
    events_summary = "\n".join([f"{event['start'].get('dateTime', event['start'].get('date'))} to {event['end'].get('dateTime', event['end'].get('date'))}: {event['summary']}" for event in events])
    
    prompt = f"""
    You are an intelligent assistant. Here are the existing events in the user's calendar:
    {events_summary}

    The user wants to add a new event with the following details:
    Summary: {summary}
    Category: {category}
    Date: {start_date} to {end_date}

    The event should be scheduled during regular hours (8 AM to 10 PM) and should be realistic for a task like '{summary}', which usually takes about 1-2 hours.
    Please suggest the optimal start and end time for this new event based on the user's current schedule and the category of the event.
    Return the format in the format: 'Start Time: 00:00', and then a new line with 'End Time: 00:00', with the zeroes seen in the example acting as placeholders.
    I only want the output specified to be printed, and nothing else. 
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an intelligent assistant."},
                {"role": "user", "content": prompt}
            ],
        )
        logging.debug(f"OpenAI response: {response}")
        return response.choices[0].message['content'].strip()
    except Exception as e:
        logging.error(f"Error calling OpenAI API: {e}")
        return "Start Time: 00:00\nEnd Time: 23:59"  # Default fallback times

def parse_suggested_time(text):
    # A simple parser to extract start and end time from OpenAI's response
    try:
        lines = text.split("\n")
        start_time = None
        end_time = None
        for line in lines:
            if "Start Time:" in line:
                start_time = line.split("Start Time: ")[1].strip()
            if "End Time:" in line:
                end_time = line.split("End Time: ")[1].strip()
        if not start_time or not end_time:
            raise ValueError("Could not parse times from response.")
        return {'startTime': start_time, 'endTime': end_time}
    except Exception as e:
        logging.error(f"Error parsing suggested time: {e}")
        return {'startTime': '00:00', 'endTime': '23:59'}  # Default fallback times

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
