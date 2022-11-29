import random
from flask import render_template, redirect, url_for, flash, request
from app import app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app.models import *
from app.forms import *
from sqlalchemy import cast, Date, desc
import datetime


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    date = datetime.date.today()
    if current_user.is_authenticated:

        post_list = []
        for followed in current_user.followed:
            for current_post in followed.posts:
                post_list.append(current_post)

        visited_genres = ListenerToGenre.query.filter_by(listener_id=current_user.id).order_by(desc('page_visit_count'))
        visited_genres_list = []

        # convert query to list
        for genre in visited_genres:
            visited_genres_list.append(genre)
        favorite_genres_temp = []
        favorite_genres = []
        all_suggested_artists = []
        suggested_artists = []

        if len(visited_genres_list) > 2:

            # process top 3
            for i in range(3):
                favorite_genres_temp.append(visited_genres_list[i])

            # get actual genres
            for genre in favorite_genres_temp:
                favorite_genres.append(Genre.query.filter_by(id=genre.genre_id).first())

            # collect all artists to be recommended
            for genre in favorite_genres:
                for current_artist in genre.artists:
                    all_suggested_artists.append(current_artist.artist)

            # remove duplicates
            all_suggested_artists = [*set(all_suggested_artists)]

            # remove already followed artists
            for current_artist in all_suggested_artists:
                if current_user.is_following(current_artist):
                    all_suggested_artists.remove(current_artist)

            # finally, generate three suggested artists
            if len(all_suggested_artists) > 2:
                suggested_artists = random.choices(all_suggested_artists, k=3)
            else:
                suggested_artists.extend(all_suggested_artists)

            return render_template('index.html', title="Home", user=current_user,
                                   date=date, posts=post_list, suggested_artists=suggested_artists)

        else:
            return render_template('index.html', title="Home", user=current_user,
                                   date=date, posts=post_list)




    else:
        return render_template('index.html', title="Home", form=SearchForm())


@app.route('/discover', methods=['GET', 'POST'])
def discover():
    default_genre_id = Genre.query.order_by('name').first().id
    default_similar_id = User.query.filter_by(type='artist').order_by('display_name').first().id

    form = DiscoverForm(genres=default_genre_id, similar_artists=default_similar_id)

    form.genres.choices = [(g.id, g.name) for g in Genre.query.order_by('name')]
    form.similar_artists.choices = [(a.id, a.display_name) for a in
                                    User.query.filter_by(type='artist').order_by('display_name')]

    if form.validate_on_submit():
        if form.discover_by.data == "Genre":
            genre_search_id = form.genres.data
            genre_search = Genre.query.filter_by(id=genre_search_id).first()
            artists = genre_search.artists
            return render_template('discover_results.html', title="Discover", artists=artists)
        if form.discover_by.data == "Similar Artist":
            artist_search_id = form.similar_artists.data
            artist_search = Artist.query.filter_by(id=artist_search_id).first()
            artists = artist_search.similar
            return render_template('discover_results_similar.html', title="Discover", artists=artists)


    return render_template('discover.html', title="Discover", form=form)


@app.route('/local', methods=['GET', 'POST'])
def local():
    form = LocalForm()
    location_search = form.location.data
    if form.validate_on_submit():
        if Artist.query.filter(Artist.location.contains(location_search)).first() is not None:
            artists = Artist.query.filter(Artist.location.contains(location_search))
            return render_template('local_results.html', title="Local Music", artists=artists)
        else:
            return render_template('local_results.html', title="Local Music")
    return render_template('local.html', title="Local Music", form=form)



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
    now = datetime.datetime.now()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ListenerRegistrationForm()
    if form.validate_on_submit():
        user = Listener(username=form.username.data, email=form.email.data, display_name=form.username.data, join_date=now,
                        bio=form.bio.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration complete!")
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register_listener.html', title='Register', form=form)


@app.route('/register_artist', methods=['GET', 'POST'])
def register_artist():
    now = datetime.datetime.now()

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = ArtistRegistrationForm()

    form.genres.choices = [(g.id, g.name) for g in Genre.query.order_by('name')]
    form.similar_artists.choices = [(a.id, a.display_name) for a in User.query.filter_by(type='artist').order_by('display_name')]

    if form.validate_on_submit():
        artist = Artist(username=form.username.data, email=form.email.data, display_name=form.display_name.data, location=form.location.data, join_date=now,
                        bio=form.bio.data)
        artist.set_password(form.password.data)
        db.session.add(artist)
        db.session.commit()
        login_user(artist)

        for genre in form.genres.data:
            genre_entry = Genre.query.filter_by(id=genre).first()
            ag = ArtistGenre(artist_id=artist.id, genre_id=genre_entry.id)
            db.session.add(ag)
            db.session.commit()

        for similar_artist in form.similar_artists.data:
            similar_entry = Artist.query.filter_by(id=similar_artist).first()
            current_user.add_similar(similar_entry)
            db.session.commit()

        flash("Registration complete!")
        return redirect(url_for('index'))

    return render_template('register_artist.html', title="Register", form=form)





@app.route('/settings')
def settings():
    return "SETTINGS"

@app.route('/artist/<name>')
@login_required
def artist(name):
    artist = Artist.query.filter_by(username=name).first()
    if artist is not None:
        followers = artist.followers
        followed = artist.followed
        display_name = artist.display_name
        genres = artist.genres

        # tracking user's frequent genres via listener_to_genre
        for genre in genres:
            listener_genre = ListenerToGenre.query.filter_by(genre_id=genre.genre.id, listener_id=current_user.id).first()
            if listener_genre is not None:

                listener_genre.page_visit_count += 1

            else:
                print(current_user.username + " / " + genre.genre.name + ": Listener Genre Link Does Not Exist")
                print("Creating Link")
                ltg_temp = ListenerToGenre(listener_id=current_user.id, genre_id=genre.genre.id, page_visit_count=1)
                db.session.add(ltg_temp)

            db.session.commit()

        return render_template('artist_page.html',
                               title="{}'s Page".format(display_name),
                               artist=artist, followers=followers, followed=followed,
                               genres=genres)
    else:
        return render_template("index.html", title="Home")


@app.route('/listener/<name>')
@login_required
def listener(name):
    listener = Listener.query.filter_by(username=name).first()
    if listener is not None:
        followers = listener.followers
        followed = listener.followed
        display_name = listener.display_name
        return render_template('listener_page.html',
                               title="{}'s Page".format(display_name),
                               listener=listener, followers=followers, followed=followed)
    else:
        return render_template("index.html", title="Home")


@app.route('/listener/<name>/edit', methods=['GET', 'POST'])
@login_required
def edit_listener(name):
    listener = Listener.query.filter_by(username=name).first()
    form = EditAccountForm(display_name=listener.display_name, bio=listener.bio)
    if listener is not None and current_user.username == listener.username:
        if form.validate_on_submit():
            current_user.display_name = form.display_name.data
            current_user.bio = form.bio.data
            db.session.commit()
            return redirect("/listener/" + listener.username)
        return render_template('edit_account.html', title="Edit Account", form=form)
    else:
        return redirect('/index')


@app.route('/artist/<name>/edit', methods=['GET', 'POST'])
@login_required
def edit_artist(name):
    artist = Artist.query.filter_by(username=name).first()
    form = EditAccountForm(display_name=artist.display_name, bio=artist.bio)
    if artist is not None and current_user.username == artist.username:
        if form.validate_on_submit():
            current_user.display_name = form.display_name.data
            current_user.bio = form.bio.data
            db.session.commit()
            return redirect("/artist/" + artist.username)
        return render_template('edit_account.html', title="Edit Account", form=form)
    else:
        return redirect('/index')


@app.route('/post/<id>', methods=['GET', 'POST'])
def post(id):
    form = CommentForm()
    post = Post.query.filter_by(id=int(id)).first_or_404()

    comments = Comment.query.filter_by(post_id=id).order_by(desc('time_posted'))

    if form.validate_on_submit():
        comment = Comment(text=form.post.data, poster_id=current_user.id, time_posted=datetime.datetime.now(), post_id=post.id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted!')
        return redirect(url_for('post', id = post.id, post=post, comments=comments))
    return render_template('post.html', title=post.text, post=post, comments=comments, form=form)

@app.route('/comment/<id>')
def comment(id):
    comment = Comment.query.filter_by(id=int(id)).first_or_404()
    original_post = Post.query.filter_by(id=comment.post_id).first()
    return render_template('comment.html', title=comment.text, comment=comment, original_post=original_post)

@app.route('/posts', methods=['GET', 'POST'])
@login_required
def posts():
    form = PostForm()
    post_list = Post.query.order_by(desc('time_posted'))

    if form.validate_on_submit():
        post = Post(text=form.post.data, poster_id=current_user.id, time_posted=datetime.datetime.now())
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return render_template('posts.html', title="Posts", posts=post_list, form=form)
    return render_template('posts.html', title="Posts", posts=post_list, form=form)

@app.route('/follow/<name>')
@login_required
def follow(name):
    if Listener.query.filter_by(username=name).first() is not None:
        user = Listener.query.filter_by(username=name).first()
        user_type = "listener"
    elif Artist.query.filter_by(username=name).first() is not None:
        user = Artist.query.filter_by(username=name).first()
        user_type = "artist"
    else:
        flash('User does not exist')
        return redirect('/index')

    if current_user.is_following(user):
        flash('You are already following this user')
        return redirect('/' + user_type + '/' + user.username)

    current_user.follow(user)
    db.session.commit()
    flash('You are now following {}!'.format(user.display_name))
    return redirect('/' + user_type + '/' + user.username)

@app.route('/unfollow/<name>')
@login_required
def unfollow(name):
    if Listener.query.filter_by(username=name).first() is not None:
        user = Listener.query.filter_by(username=name).first()
        user_type = "listener"
    elif Artist.query.filter_by(username=name).first() is not None:
        user = Artist.query.filter_by(username=name).first()
        user_type = "artist"
    else:
        flash('User does not exist')
        return redirect('/index')

    if not current_user.is_following(user):
        flash('You are not following this user')
        return redirect('/' + user_type + '/' + user.username)

    current_user.unfollow(user)
    db.session.commit()
    flash('You are no longer following {}'.format(user.display_name))
    return redirect('/' + user_type + '/' + user.username)


@app.route('/resetDB')
def resetDB():

    reset_db()

    return "DB RESET"

@app.route('/populate_db')
def populate_db():

    # reset the DB
    reset_db()

    # local datetime.now var for setting join dates
    now = datetime.datetime.now()

    # declare genres
    genre1 = Genre(name="Pop")
    genre2 = Genre(name="Electronica")
    genre3 = Genre(name="Folk")
    genre4 = Genre(name="Rock")
    genre5 = Genre(name="Soundtrack")
    genre6 = Genre(name="Classical")
    genre7 = Genre(name="World")
    genre8 = Genre(name="Rap")
    genre9 = Genre(name="R&B")
    genre10 = Genre(name="Country")

    db.session.add_all([genre1, genre2, genre3, genre4, genre5,
                        genre6, genre7, genre8, genre9, genre10])
    db.session.commit()

    # declare users
    user1 = Listener(username="user1", email="user1@resonate.net",
                     display_name="User 1", join_date=now,
                     bio="Bio Text Here")
    user1.set_password("password1")

    user2 = Listener(username="user2", email="user2@resonate.net",
                     display_name="User 2", join_date=now,
                     bio="Bio Text Here"
                     )
    user2.set_password("password2")

    user3 = Artist(username="user3", email="user3@resonate.net",
                   display_name="The Cool Band", join_date=now,
                   location="Ithaca, NY", bio="Bio Text Here")
    user3.set_password("password3")

    user4 = Artist(username="user4", email="user4@resonate.net",
                   display_name="The Very Cool Band", join_date=now,
                   location="Hell, MI", bio="Bio Text Here")
    user4.set_password("password4")

    user5 = Artist(username="user5", email="user5@resonate.net",
                   display_name="User 5", join_date=now,
                   location="Antarctica", bio="Bio Text Here")
    user5.set_password("password5")

    user6 = Listener(username="krb", email="krb@krb.net",
                     display_name="KRB", join_date=now, bio="Bio Text Here")
    user6.set_password("krb")

    user7 = Artist(username="user7", email="user7@resonate.net",
                   display_name="Another Band", join_date=now,
                   location="Ithaca, NY", bio="Bio Text Here")
    user7.set_password("password7")

    user8 = Artist(username="user8", email="user8@resonate.net",
                   display_name="Maybe Not a Band", join_date=now,
                   location="Island of Ithaca, Greece", bio="Bio Text Here")
    user8.set_password("password8")

    db.session.add_all([user1, user2, user3, user4, user5, user6,
                        user7, user8])
    db.session.commit()

    # declare artist genres
    ag1 = ArtistGenre(artist_id=user3.id, genre_id=genre1.id)
    ag2 = ArtistGenre(artist_id=user3.id, genre_id=genre2.id)
    ag3 = ArtistGenre(artist_id=user4.id, genre_id=genre10.id)
    ag4 = ArtistGenre(artist_id=user4.id, genre_id=genre9.id)
    ag5 = ArtistGenre(artist_id=user5.id, genre_id=genre5.id)
    ag6 = ArtistGenre(artist_id=user5.id, genre_id=genre6.id)
    ag7 = ArtistGenre(artist_id=user5.id, genre_id=genre7.id)
    ag8 = ArtistGenre(artist_id=user7.id, genre_id=genre2.id)
    ag9 = ArtistGenre(artist_id=user7.id, genre_id=genre3.id)
    ag10 = ArtistGenre(artist_id=user8.id, genre_id=genre8.id)
    ag11 = ArtistGenre(artist_id=user8.id, genre_id=genre5.id)
    ag12 = ArtistGenre(artist_id=user8.id, genre_id=genre7.id)

    db.session.add_all([ag1, ag2, ag3, ag4, ag5, ag6, ag7,
                        ag8, ag9, ag10, ag11, ag12])
    db.session.commit()

    # declare user frequent artists
    atl1 = ArtistToListener(listener_id=user1.id,artist_id=user3.id,page_visit_count=50)
    atl2 = ArtistToListener(listener_id=user1.id, artist_id=user4.id, page_visit_count=100)
    atl3 = ArtistToListener(listener_id=user1.id, artist_id=user5.id, page_visit_count=150)
    atl4 = ArtistToListener(listener_id=user2.id, artist_id=user4.id, page_visit_count=500)
    atl5 = ArtistToListener(listener_id=user6.id, artist_id=user3.id, page_visit_count=100)
    atl6 = ArtistToListener(listener_id=user6.id, artist_id=user5.id, page_visit_count=120)
    atl7 = ArtistToListener(listener_id=user3.id, artist_id=user5.id, page_visit_count=50)
    atl8 = ArtistToListener(listener_id=user4.id, artist_id=user3.id, page_visit_count=200)

    db.session.add_all([atl1, atl2, atl3, atl4, atl5, atl6, atl7, atl8])
    db.session.commit()

    # declare user frequent genres
    ltg1 = ListenerToGenre(listener_id=user1.id, genre_id=genre1.id, page_visit_count=80)
    ltg2 = ListenerToGenre(listener_id=user1.id, genre_id=genre8.id, page_visit_count=200)
    ltg3 = ListenerToGenre(listener_id=user2.id, genre_id=genre7.id, page_visit_count=700)
    ltg4 = ListenerToGenre(listener_id=user2.id, genre_id=genre6.id, page_visit_count=150)
    ltg5 = ListenerToGenre(listener_id=user2.id, genre_id=genre3.id, page_visit_count=200)
    ltg6 = ListenerToGenre(listener_id=user3.id, genre_id=genre5.id, page_visit_count=400)
    ltg7 = ListenerToGenre(listener_id=user4.id, genre_id=genre2.id, page_visit_count=250)
    ltg8 = ListenerToGenre(listener_id=user4.id, genre_id=genre10.id, page_visit_count=60)
    ltg9 = ListenerToGenre(listener_id=user5.id, genre_id=genre4.id, page_visit_count=900)
    ltg10 = ListenerToGenre(listener_id=user6.id, genre_id=genre2.id, page_visit_count=200)
    ltg11 = ListenerToGenre(listener_id=user6.id, genre_id=genre3.id, page_visit_count=140)
    ltg12 = ListenerToGenre(listener_id=user6.id, genre_id=genre4.id, page_visit_count=70)

    db.session.add_all([ltg1, ltg2, ltg3, ltg4, ltg5, ltg6,
                        ltg7, ltg8, ltg9, ltg10, ltg11, ltg12])
    db.session.commit()

    # declare posts
    post1 = Post(poster_id=user1.id,title="This is a cool post",
                 text="I don't have too much to say but yea this is definitely"
                      "one of the posts ever. Definitely.",
                 time_posted=now)
    post2 = Post(poster_id=user3.id, title="Guys I just made a post",
                 text="I think you're reading it right now, but I might be"
                      "entirely wrong. Might wanna check up on that at some"
                      "point, but I can't tell you what to do or anything.",
                 time_posted=now)
    post3 = Post(poster_id=user3.id, title="Stuff I forgot to say in my last post",
                 text="Okay I'll be honest there wasn't actually anything I"
                      "forgot to say I just wanted to make another post.",
                 time_posted=now)
    post4 = Post(poster_id=user5.id, title="I'm running out of post titles",
                 text="I've written like four of these things by now. That's like,"
                      "more than 3. Geez.",
                 time_posted=now)
    post5 = Post(poster_id=user6.id, title="This is the last post!",
                 text="Finally, at long last, I've reached the end of my long"
                      "posting journey. I shall post no more and soon I will"
                      "be at rest.",
                 time_posted=now)
    post6 = Post(poster_id=user6.id, title=":)",
                 text="ok I lied about that being my last post",
                 time_posted=now)

    db.session.add_all([post1, post2, post3, post4, post5, post6])
    db.session.commit()

    # declare comments
    comment1 = Comment(post_id=post2.id, poster_id=user2.id,
                       text="that's so cool", time_posted=now)
    comment2 = Comment(post_id=post3.id, poster_id=user4.id,
                       text="it's okay we all make mistakes sometimes", time_posted=now)
    comment3 = Comment(post_id=post6.id, poster_id=user1.id,
                       text="I am very upset and infuriated", time_posted=now)
    comment4 = Comment(post_id=post6.id, poster_id=user5.id,
                       text="ok rude", time_posted=now)

    db.session.add_all([comment1, comment2, comment3, comment4])
    db.session.commit()

    # make some users follow eachother
    user1.follow(user3)
    user1.follow(user4)
    user1.follow(user6)
    user2.follow(user5)
    user2.follow(user1)
    user3.follow(user2)
    user3.follow(user4)
    user4.follow(user6)
    user5.follow(user2)
    user5.follow(user4)
    user5.follow(user1)
    user6.follow(user2)

    db.session.commit()

    # add some similar artists
    user3.add_similar(user4)
    user5.add_similar(user3)
    user4.add_similar(user3)
    user3.add_similar(user5)

    db.session.commit()

    # flash message / return to index
    flash('Populated database with default data')
    return render_template('base.html', title='Populated')


def reset_db():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table {}'.format(table))
        db.session.execute(table.delete())
    db.session.commit()
