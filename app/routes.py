from flask import render_template, redirect, url_for, flash, request
from app import app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app.models import *
from app.forms import *
import datetime


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title="Home")


@app.route('/discover')
def discover():
    return "DISCOVER"


@app.route('/local')
def local():
    return "LOCAL MUSIC"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register')
def register():
    return render_template('register.html')
@app.route('/register_listener', methods=['GET', 'POST'])
def register_listener():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = ListenerRegistrationForm()
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            listener = Listener(id=user.id)
            db.session.add(listener)
            db.session.commit()
            flash("Registration complete!")
            login_user(user)
            return redirect(url_for('index'))
        return render_template('register_listener.html', title='Register', form=form)


@app.route('/register_artist', methods=['GET', 'POST'])
def register_artist():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ArtistRegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        artist = Artist(id=user.id, location=form.location.data)
        db.session.add(artist)
        db.session.commit()
        flash("Registration complete!")
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register_artist.html', title='Register', form=form)





@app.route('/settings')
def settings():
    return "SETTINGS"

@app.route('/artist/<name>')
@login_required
def artist(name):
    return "ARTIST PAGE"


@app.route('/listener/<name>')
@login_required
def listener(name):
    return "LISTENER PAGE"

@app.route('/resetDB')
def resetDB():

    reset_db()

    return "DB RESET"

def reset_db():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table {}'.format(table))
        db.session.execute(table.delete())
    db.session.commit()