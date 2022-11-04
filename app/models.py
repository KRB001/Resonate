from sqlalchemy import cast
from sqlalchemy.orm import relationship

from app import db, login # TO DO SOON: add db and login setup stuff to __init.py__
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), index=True, unique=True)
    email = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(128))
    display_name = db.Column(db.String(100), index=True)
    join_date = db.Column(db.DateTime)
    profile_public = db.Column(db.Boolean)
    following_public = db.Column(db.Boolean)
    # other settings for any account type go here

    followers = relationship(
        "Follows",
        primaryjoin=id == id,
        foreign_keys=id,
        remote_side=id,
    )
    followed_accounts = relationship(
        "Follows",
        primaryjoin=id == id,
        foreign_keys=id,
        remote_side=id,
    )
    frequent_artists = db.relationship('ArtistToListener', backref='listener', lazy='dynamic')
    frequent_genres = db.relationship('ListenerToGenre', backref='listener', lazy='dynamic')

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Listener(User, db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    # listener only settings/info goes here

    def __repr__(self):
        return '<Listener {}>'.format(self.username)



class Artist(User, db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    location = db.Column(db.String(200), index=True)
    # other artist only settings/info goes here

    similar = relationship(
        "SimilarArtist",
        primaryjoin=id == id,
        foreign_keys=id,
        remote_side=id,
    )
    referenced_similar = relationship(
        "SimilarArtist",
        primaryjoin=id == id,
        foreign_keys=id,
        remote_side=id,
    )

    genres = db.relationship('ArtistGenre', backref='artist', lazy='dynamic')
    albums = db.relationship('ArtistToAlbum', backref='featured_artist', lazy='dynamic')
    songs = db.relationship('ArtistToSong', backref='song_creator', lazy='dynamic')
    frequent_viewers = db.relationship('ArtistToListener', backref='visited_artist', lazy='dynamic')

    def __repr__(self):
        return '<Artist {}>'.format(self.username)

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    artists = db.relationship('ArtistGenre', backref='genre', lazy='dynamic')
    frequent_listeners = db.relationship('ListenerToGenre', backref='frequent_genre', lazy='dynamic')
    def __repr__(self):
        return '<Genre {}>'.format(self.name)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poster_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(200), index=True)
    text = db.Column(db.String(1000), index=True)
    time_posted = db.Column(db.DateTime, index=True)

    def __repr__(self):
        return '<Post {}>'.format(self.text)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    poster_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.String(1000), index=True)
    time_posted = db.Column(db.DateTime, index=True)

    def __repr__(self):
        return '<Comment {}>'.format(self.text)


class Album (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True, unique=True)
    release_date = db.Column(db.DateTime, index=True)
    description = db.Column(db.String(1000), index=True)
    artists = db.relationship('ArtistToAlbum', backref='album', lazy='dynamic')
    songs = db.relationship('SongToAlbum', backref='album', lazy='dynamic')

    def __repr__(self):
        return '<Album {}>'.format(self.name)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True, unique=True)
    length = db.Column(db.String(25))
    release_date = db.Column(db.DateTime, index=True)
    artists = db.relationship('ArtistToSong', backref='song', lazy='dynamic')
    albums = db.relationship('SongToAlbum', backref='song', lazy='dynamic')

    def __repr__(self):
        return '<Song {}>'.format(self.name)

class Follows(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class ArtistGenre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=False)

class SimilarArtist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    similar_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)

class ArtistToListener(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # this is left as generic user so artists can get recs for other artists
    listener_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    page_visit_count = db.Column(db.Integer)


class ListenerToGenre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listener_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=False)
    page_visit_count = db.Column(db.Integer)

class ArtistToAlbum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)


class ArtistToSong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)


class SongToAlbum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)

