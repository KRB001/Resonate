from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, DateField, PasswordField, BooleanField, \
    SelectMultipleField, SelectField, RadioField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User, Listener, Artist


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class ListenerRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_password = PasswordField("Repeat Password", validators=[DataRequired(),EqualTo('password')])
    bio = TextAreaField('User Bio')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user != None:
            raise ValidationError("Username already taken.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user != None:
            raise ValidationError("Email associated with another account. Please use a different email.")


class ArtistRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    display_name = StringField('Artist Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_password = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo('password')])
    location = StringField('Location', validators=[DataRequired()])
    bio = TextAreaField('User Bio')
    genres = SelectMultipleField('Genre tags', validators=[DataRequired()], coerce=int)
    similar_artists = SelectMultipleField('Similar Artists (select up to 3)', coerce=int)
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user != None:
            raise ValidationError("Username already taken.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user != None:
            raise ValidationError("Email associated with another account. Please use a different email.")

    def validate_similar_artists(self, similar_artists):
        if len(similar_artists.data) > 3:
            raise ValidationError("Please only choose 3 similar artists.")


class LocalForm(FlaskForm):
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired()])
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    post = TextAreaField('Reply', validators=[DataRequired()])
    submit = SubmitField('Submit')


class DiscoverForm(FlaskForm):
    discover_by = RadioField('Discover by...', choices=['Genre', 'Similar Artist'])
    genres = SelectField('Genres', validators=[DataRequired()], coerce=int)
    similar_artists = SelectField('Similar Artists', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    search_term = TextAreaField('What are you looking for?', validators=[DataRequired()])
    submit = SubmitField('Search')


class EditAccountForm(FlaskForm):
    display_name = StringField('Display Name', validators=[DataRequired()])
    bio = TextAreaField('User Bio')
    submit = SubmitField('Submit')