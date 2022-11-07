from flask import render_template, redirect, url_for, flash, request
from app import app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app.models import *
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


@app.route('/login')
def login():
    return render_template('login.html', title="Login")


@app.route('/register')
def register():
    return "REGISTER"


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

@app.route('/reset_db')
def reset_db():

    reset_db()

    return "DB RESET"

@app.route('/populate_db')
def populate_db():

    reset_db()

    now = datetime.datetime.now()

    user1 = Listener(username="user1", email="user1@resonate.net",
                     display_name="User 1", join_date=now
                     )
    user1.set_password("password1")

    user2 = Listener(username="user2", email="user2@resonate.net",
                     display_name="User 2", join_date=now
                     )
    user2.set_password("password2")

    user3 = Artist(username="user3", email="user3@resonate.net",
                     display_name="The Cool Band", join_date=now,
                   location="Ithaca, NY")
    user3.set_password("password3")

    user4 = Artist(username="user4", email="user4@resonate.net",
                   display_name="The Very Cool Band", join_date=now,
                   location="Hell, MI")
    user4.set_password("password4")

    db.session.add_all([user1, user2, user3, user4])
    db.session.commit()



    genre1 = Genre(name="Pop")
    genre2 = Genre(name="Electronica")
    genre3 = Genre(name="Folk")
    genre4 = Genre(name="Rock")
    genre5 = Genre(name="Soundtrack")

    db.session.add_all([genre1, genre2, genre3, genre4, genre5])
    db.session.commit()



    return "DB POPULATED"

def reset_db():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table {}'.format(table))
        db.session.execute(table.delete())