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