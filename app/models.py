from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    username = db.Column(db.String(100), index=True, unique=True)
    email = db.Column(db.String(120), unique=True)
    bio = db.Column(db.String(1000))
    pw_hash = db.Column(db.String(128))
    display_name = db.Column(db.String(100), index=True)
    join_date = db.Column(db.DateTime)
    profile_public = db.Column(db.Boolean)
    following_public = db.Column(db.Boolean)
    # other settings for any account type go here

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    requests = db.relationship('Request', backref='requester', lazy='dynamic')

    frequent_artists = db.relationship('ArtistToListener', backref='listener', lazy='dynamic')
    frequent_genres = db.relationship('ListenerToGenre', backref='listener', lazy='dynamic')

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        "polymorphic_on": type
    }

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def __repr__(self):
        return '<User {}>'.format(self.username)



@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Listener(User, db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    # listener only settings/info goes here

    __mapper_args__ = {
        'polymorphic_identity': 'listener',
        'with_polymorphic': '*'
    }

    def __repr__(self):
        return '<Listener {}>'.format(self.username)


similar_artists = db.Table('similar_artists',
                           db.Column('referenced_artist_id', db.Integer, db.ForeignKey('artist.id')),
                           db.Column('similar_artist_id', db.Integer, db.ForeignKey('artist.id'))
)


class Artist(User, db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    location = db.Column(db.String(200), index=True)
    # other artist only settings/info goes here

    similar = db.relationship(
        'Artist', secondary=similar_artists,
        primaryjoin=(similar_artists.c.referenced_artist_id == id),
        secondaryjoin=(similar_artists.c.similar_artist_id == id),
        backref=db.backref('similar_to', lazy='dynamic'), lazy='dynamic')

    genres = db.relationship('ArtistGenre', backref='artist', lazy='dynamic')
    albums = db.relationship('ArtistToAlbum', backref='featured_artist', lazy='dynamic')
    songs = db.relationship('ArtistToSong', backref='song_creator', lazy='dynamic')
    frequent_viewers = db.relationship('ArtistToListener', backref='visited_artist', lazy='dynamic')

    __mapper_args__ = {
        'polymorphic_identity': 'artist',
        'with_polymorphic': '*'
    }

    def add_similar(self, artist):
        if not self.is_similar(artist):
            self.similar.append(artist)

    def remove_similar(self, artist):
        if self.is_similar(artist):
            self.similar.remove(artist)

    def is_similar(self, artist):
        return self.similar.filter(
            similar_artists.c.similar_artist_id == artist.id).count() > 0

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





class ArtistGenre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=False)

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


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    subject = db.Column(db.String(144), index=True, unique=True)
    description = db.Column(db.String(2056), index=True, unique=True)
    category = db.Column(db.String(64), index=True, unique=True)

