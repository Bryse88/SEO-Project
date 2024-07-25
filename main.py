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
from datetime import datetime, timedelta

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

    # Identifier for events created from the webpage
    identifier = "CreatedFromWebpage"

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
                events_result = service.events().list(calendarId='primary', timeMin=f"{start_date}T00:00:00Z", timeMax=f"{end_date}T23:59:59Z", singleEvents=True, orderBy='startTime').execute()
                events = events_result.get('items', [])

                openai_response = generate_chat_response(events, summary, category, description, start_date, end_date)
                logging.debug(f"AI response: {openai_response}")
                suggested_time = parse_suggested_time(openai_response)
                start_time, end_time = suggested_time['startTime'], suggested_time['endTime']
                flash(f'Suggested time by AI: Start: {start_time}, End: {end_time}', 'info')

            except Exception as e:
                logging.error(f"Error fetching AI suggestion: {e}")
                flash(f'An error occurred while fetching AI suggestion: {e}', 'error')
                return redirect(url_for('notes'))

        if not validate_time(start_time, end_time):
            flash('Event time must be between 8 AM and 10 PM and not overlap with existing events.', 'error')
            return redirect(url_for('notes'))

        start = f"{start_date}T{format_time(start_time)}"
        end = f"{end_date}T{format_time(end_time)}"
        event = {
            'summary': summary,
            'description': f"{description}\n{identifier}",  # Add identifier to description
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

def format_time(time_str):
    """Ensure the time string is in '%H:%M:%S' format."""
    if len(time_str) == 5:
        time_str += ":00"
    return time_str

def validate_time(start_time, end_time):
    try:
        start_dt = datetime.strptime(format_time(start_time), '%H:%M:%S')
        end_dt = datetime.strptime(format_time(end_time), '%H:%M:%S')
        if start_dt.time() < datetime.strptime("08:00:00", '%H:%M:%S').time() or end_dt.time() > datetime.strptime("22:00:00", '%H:%M:%S').time():
            return False
        return True
    except Exception as e:
        logging.error(f"Error validating time: {e}")
        return False


def generate_chat_response(events, summary, category, description, start_date, end_date):
    events_summary = "\n".join([f"{event['start'].get('dateTime', event['start'].get('date'))} to {event['end'].get('dateTime', event['end'].get('date'))}: {event['summary']}" for event in events])
    
    prompt = f"""
    You are an intelligent assistant. Here are the existing events in the user's calendar for the date {start_date}:
    {events_summary}

    The user wants to add a new event with the following details:
    Title: {summary}
    Description: {description}
    Category: {category}
    Date: {start_date} to {end_date}

    The event should be scheduled during regular hours (8 AM to 10 PM) and should be realistic for a task like '{summary}', which usually takes about 1-2 hours.
    Ensure that the new event does not overlap with any existing events in the user's calendar.
    Please suggest the optimal start and end time for this new event based on the user's current schedule and the category of the event.
    Return the times in the format: 'Start Time: HH:MM AM/PM', followed by a new line with 'End Time: HH:MM AM/PM'.
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


def parse_suggested_time(ai_response):
    try:
        lines = ai_response.strip().split('\n')
        # Locate the lines containing "Start Time" and "End Time"
        start_time_line = next(line for line in lines if "Start Time" in line)
        end_time_line = next(line for line in lines if "End Time" in line)
        start_time_str = start_time_line.split(": ")[1].strip().replace('**', '')
        end_time_str = end_time_line.split(": ")[1].strip().replace('**', '')

        # Ensure correct time format
        start_time = datetime.strptime(start_time_str, '%I:%M %p').strftime('%H:%M:%S')
        end_time = datetime.strptime(end_time_str, '%I:%M %p').strftime('%H:%M:%S')

        return {'startTime': start_time, 'endTime': end_time}
    except Exception as e:
        logging.error(f"Error parsing suggested time: {e}")
        return {'startTime': '00:00:00', 'endTime': '23:59:59'}  # Default fallback times


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/completed_notes')
def completed_notes():
    identifier = "CreatedFromWebpage"
    try:
        credentials = Credentials(session['google_token'][0])
        service = build('calendar', 'v3', credentials=credentials)
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(calendarId='primary', timeMin=now, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        # Filter events with the specific identifier
        completed_events = [event for event in events if identifier in event.get('description', '')]
        return render_template('completed_notes.html', events=completed_events, category_colors=CATEGORY_COLORS)
    except Exception as e:
        logging.error(f"Error retrieving events: {e}")
        flash(f'An error occurred: {e}', 'error')
        return redirect(url_for('index'))


# Add this filter to your Flask app
@app.template_filter('format_datetime')
def format_datetime(value):
    """Format a datetime string to a more readable format"""
    if 'T' in value:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return dt.strftime('%A, %B %d, %Y at %I:%M %p')
    else:
        dt = datetime.fromisoformat(value)
        return dt.strftime('%A, %B %d, %Y')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5050)
