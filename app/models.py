from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    instruments = db.relationship('Instrument', backref='venue', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Instrument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(64), index=True, unique=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    defaultGoalInSeconds = db.Column(db.Integer)
    regiments = db.relationship('Regiment', backref='venue', lazy='dynamic')


class Regiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    warmups = db.Column(db.Text)
    repertoire = db.Column(db.Text)
    goalInSeconds = db.Column(db.Integer)
    timeElapsedInSeconds = db.Column(db.Integer)
    instrumentId = db.Column(db.Integer, db.ForeignKey('instrument.id'))


# User<Instrument<Regiment, where carats are one-to-many relationships