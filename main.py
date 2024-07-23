import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, session, request, render_template, flash, jsonify
from flask_oauthlib.client import OAuth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from forms import RegistrationForm
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
import secrets

load_dotenv()

app = Flask(__name__)
bootstrap = Bootstrap(app)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///collaboration.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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

@app.before_request
def before_request():
    if not hasattr(app, 'db_initialized'):
        with app.app_context():
            db.create_all()
            app.db_initialized = True

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
    user_info = google.get('userinfo')
    email = user_info.data['email']
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email)
            db.session.add(user)
            db.session.commit()
    session['user_email'] = email
    return redirect(url_for('notes'))

@app.route('/add_note', methods=['POST'])
def add_note():
    note_text = request.json.get('note')
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'status': 'failure', 'message': 'User not authenticated'}), 403
    with app.app_context():
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({'status': 'failure', 'message': 'User not found'}), 404
        note = Note(text=note_text, author=user)
        db.session.add(note)
        db.session.commit()
        return jsonify({'status': 'success', 'note': {'text': note.text, 'author': user.email}}), 201

@app.route('/delete_note', methods=['POST'])
def delete_note():
    note_text = request.json.get('note')
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'status': 'failure', 'message': 'User not authenticated'}), 403
    with app.app_context():
        note = Note.query.filter_by(text=note_text).first()
        if note:
            db.session.delete(note)
            db.session.commit()
            return jsonify({'status': 'success', 'note': note_text}), 200
        return jsonify({'status': 'failure', 'message': 'Note not found'}), 404

@app.route('/update_note', methods=['POST'])
def update_note():
    old_note_text = request.json.get('oldNote')
    new_note_text = request.json.get('newNote')
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'status': 'failure', 'message': 'User not authenticated'}), 403
    with app.app_context():
        note = Note.query.filter_by(text=old_note_text).first()
        if note:
            note.text = new_note_text
            db.session.commit()
            return jsonify({'status': 'success', 'note': new_note_text}), 200
        return jsonify({'status': 'failure', 'message': 'Note not found'}), 404

@app.route('/get_notes', methods=['GET'])
def get_notes():
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'status': 'failure', 'message': 'User not authenticated'}), 403
    with app.app_context():
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({'status': 'failure', 'message': 'User not found'}), 404
        notes = user.notes + [collaboration.note for collaboration in user.collaborations]
        notes_data = [{'text': note.text, 'author': note.author.email} for note in notes]
        return jsonify({'notes': notes_data}), 200

@app.route('/invite_collaborator', methods=['POST'])
def invite_collaborator():
    invitee_email = request.json.get('invitee')
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'status': 'failure', 'message': 'User not authenticated'}), 403
    with app.app_context():
        invitee = User.query.filter_by(email=invitee_email).first()
        if not invitee:
            invitee = User(email=invitee_email)
            db.session.add(invitee)
            db.session.commit()
        user = User.query.filter_by(email=user_email).first()
        notes = user.notes
        for note in notes:
            if not Collaboration.query.filter_by(note_id=note.id, collaborator_id=invitee.id).first():
                collaboration = Collaboration(note_id=note.id, collaborator_id=invitee.id)
                db.session.add(collaboration)
                db.session.commit()
        return jsonify({'status': 'success', 'invitee': invitee_email}), 200

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5050)
