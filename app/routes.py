from flask import render_template, redirect, flash, request, url_for
from flask_wtf import FlaskForm
from werkzeug.urls import url_parse
from wtforms import StringField
from app import app, db
from app.models import User, Instrument, Regiment
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegimentForm, RegistrationForm


@app.route('/')
@app.route('/index')
def index():
    return render_template('base.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/index')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/index')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect('/login')
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    form.instruments.choices = [(i.id, i.label) for i in Instrument.query.order_by('label').all()]
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        instrumentsIn = form.instruments.data.split("\n")
        for instrumentIn in instrumentsIn:
            db.session.add(Instrument(
                label=instrumentIn,
                userId=user.id
            ))

        flash('New user registered')
        return redirect(url_for('defaultGoals'))
    return render_template('register.html', title='Register', form=form)


@app.route('/defaultGoals', methods=['GET', 'POST'])
def defaultGoals():
    class Form(FlaskForm):
        pass
    for instrument in User.instruments:
        setattr(Form, instrument.id, StringField(instrument.label + " (Declare in hh:mm)"))
    form = Form()
    if form.validate_on_submit():
        for instrument in User.instruments:
            hourMin = getattr(form, instrument.label).data.split(":")
            instrument.defaultGoalInSeconds = hourMin[0]*60+hourMin[1]
        return redirect('/index')
    return render_template('defaultGoals.html', title='Set Default Goals')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', title='404 Error'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html', title='500 Error'), 500