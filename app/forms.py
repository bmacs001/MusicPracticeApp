from flask_wtf import FlaskForm
from wtforms import \
    StringField, SubmitField, PasswordField, BooleanField, TextAreaField
from wtforms.fields.html5 import IntegerField
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
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class InstrumentForm(FlaskForm):
    instruments = TextAreaField('Input Instruments To Practice (Separate with line breaks)')
    submit = SubmitField('Submit')


class RegimentForm(FlaskForm):
    warmups = TextAreaField('Warmup')
    repertoire = TextAreaField('Repertoire')
    goalMin = IntegerField('Custom Goal')
    goalHour = IntegerField('Custom Goal')
    submit = SubmitField('Submit')