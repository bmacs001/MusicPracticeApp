from flask_wtf import FlaskForm
from wtforms import \
    StringField, SubmitField, PasswordField, BooleanField, SelectField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    instruments = TextAreaField('Instruments (Separate with line breaks)')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class RegimentForm(FlaskForm):
    date = DateField('Date')
    instrument = SelectField('Instrument', coerce=int)
    warmups = TextAreaField('Warmup')
    repertoire = TextAreaField('Repertoire')
    goal = StringField('Custom Goal (hh:mm)')