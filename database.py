from flask_sqlalchemy import SQLAlchemy

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    notes = db.relationship('Note', backref='author', lazy=True)
    collaborations = db.relationship('Collaboration', backref='collaborator', lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    collaborations = db.relationship('Collaboration', backref='note', lazy=True)

class Collaboration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable=False)
    collaborator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
