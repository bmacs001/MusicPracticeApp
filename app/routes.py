from datetime import date

from flask import render_template, redirect, flash, request, url_for
from flask_wtf import FlaskForm
from werkzeug.urls import url_parse
from wtforms import SubmitField
from wtforms.fields.html5 import DateField, IntegerField
from wtforms.validators import DataRequired

from app import app, db
from app.models import User, Instrument, Regiment
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegimentForm, RegistrationForm, InstrumentForm


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/logout')
@login_required
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
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('New user registered.')
        return redirect(url_for('setInstruments'))
    return render_template('register.html', title='Register', form=form)


@app.route('/setInstruments', methods=['GET', 'POST'])
@login_required
def setInstruments():
    form = InstrumentForm()
    output = ""
    for instrumentOut in current_user.instruments:
        output+=str(instrumentOut.label)+"\r\n"
    form.instruments.data = output
    if form.validate_on_submit():
        instrumentsIn = str(form.instruments.data).split("\r\n")
        for instrumentIn in instrumentsIn:
            if next((i for i in current_user.instruments if i.label == instrumentIn), None) is None \
                    and instrumentIn != '':
                db.session.add(Instrument(
                    label=instrumentIn,
                    userId=current_user.id
                ))
        db.session.commit()
        return redirect(url_for('defaultGoals'))
    return render_template('setInstruments.html', title='Set Instruments', form=form)


@app.route('/defaultGoals', methods=['GET', 'POST'])
@login_required
def defaultGoals():
    class FormClass(FlaskForm):
        submit = SubmitField('Submit')
    for instrument in current_user.instruments:
        setattr(FormClass, instrument.label + "TimeHour", IntegerField())
        setattr(FormClass, instrument.label + "TimeMin", IntegerField())
    form = FormClass()
    if form.validate_on_submit():
        for instrument in current_user.instruments:
            min = 0
            if getattr(form, instrument.label+"TimeHour").data is not None:
                min+=getattr(form, instrument.label+"TimeHour").data*60
            if getattr(form, instrument.label+"TimeMin").data is not None:
                min+=getattr(form, instrument.label+"TimeMin").data
            instrument.defaultGoalInMinutes = min
        db.session.commit()
        flash("Default practice times for each instrument have been recorded. Review your changes in your Account page")
        return redirect('/index')
    return render_template('defaultGoals.html', title='Set Default Goals', form=form, instruments=current_user.instruments)


@app.route('/practice')
@login_required
def practiceHome():
    today = date.today()
    return render_template('practiceHome.html', title='Practice', instruments=current_user.instruments, today=today)


@app.route('/practice/<instrument>', methods=['GET', 'POST'])
@login_required
def practice(instrument):
    today = date.today()
    instrumentIn = next((i for i in current_user.instruments if i.label == instrument), None)
    regimentIn = next((i for i in instrumentIn.regiments if i.date == today), None)
    if regimentIn is None:
        regimentIn = Regiment(
            date=today,
            goalInMinutes=instrumentIn.defaultGoalInMinutes,
            instrumentId = instrumentIn.id,
            timeElapsedInSeconds=0
        )
        db.session.add(regimentIn)
        db.session.commit()
    return render_template('practice.html', title='Practice', instruments=current_user.instruments, today=today,
                           instrumentIn=instrumentIn, regimentIn=regimentIn)


@app.route('/account')
@login_required
def account():
    return render_template('account.html')


@app.route('/calendar')
@login_required
def calendar():
    class FormClass(FlaskForm):
        dayIn = DateField('Select Date', validators=[DataRequired()])
    setattr(FormClass, "submit", SubmitField('Select'))
    form = FormClass()
    if form.validate_on_submit():
        return redirect('/calendar/' + form.dayIn.data)
    return render_template('calendar.html', form=form)


@app.route('/calendar/<date>')
@login_required
def calendarOnDate(date):
    return render_template('calendarBydate.html', date=date)


@app.route('/calendar/<date>/<instrument>')
@login_required
def viewRegiment(date, instrument):
    instrumentIn = next((i for i in current_user.instruments if i.label == instrument), None)
    regimentIn = next((i for i in instrumentIn.regiments if i.date == date), None)
    if regimentIn is None:
        regimentIn = Regiment(
            date=date,
            goalInMinutes=instrumentIn.defaultGoalInMinutes
        )
    return render_template('viewRegiment.html', instrumentIn=instrumentIn, regimentIn=regimentIn, date=date)


@app.route('/calendar/<date>/<instrument>/edit')
@login_required
def editRegiment(date, instrument):
    instrumentIn = next((i for i in current_user.instruments if i.label == instrument), None)
    regimentIn = next((i for i in instrumentIn.regiments if i.date == date), None)
    form = RegimentForm()
    if regimentIn is None:
        form.goalMin.data=instrumentIn.defaultGoalInMinutes%60
        form.goalHour.data=instrumentIn.defaultGoalInMinutes/60
    else:
        form.goalMin.data=regimentIn.goalInMinutes%60
        form.goalHour.data = regimentIn.goalInMinutes/60
        form.warmups.data = regimentIn.warmpus
        form.repertoire.data = regimentIn.repertoire
    if form.validate_on_submit():
        if regimentIn is None:
            regimentIn = Regiment(
                date=date,
                instrumentId=instrumentIn.id,
                warmups=form.warmups.data,
                repertoire=form.repertoire.data,
                goalInMinutes=form.goalMin.data+form.goalHour.data*60,
                timeElapsedInSeconds=0
            )
            db.session.add(regimentIn)
        else:
            regimentIn.warmups=form.warmups.data
            regimentIn.repertoire=form.repertoire.data
            regimentIn.goalInMinutes=form.goalMin.data+form.goalHour.data*60
        db.session.commit()
        return redirect('/calendar/' + date + '/' + instrument)
    return render_template('editRegiment.html', form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', title='404 Error'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html', title='500 Error'), 500