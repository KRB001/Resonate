from flask import render_template, redirect, url_for, flash, request
from app import app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app.models import *
import datetime


@app.route('/')
@app.route('/index')
def index():
    return "INDEX"


@app.route('/discover')
def discover():
    return "DISCOVER"

