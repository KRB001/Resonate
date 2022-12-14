"""empty message

Revision ID: d147c11e31fb
Revises: 
Create Date: 2022-12-08 10:53:30.889754

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd147c11e31fb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('album',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.Column('release_date', sa.DateTime(), nullable=True),
    sa.Column('description', sa.String(length=1000), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_album_description'), 'album', ['description'], unique=False)
    op.create_index(op.f('ix_album_name'), 'album', ['name'], unique=True)
    op.create_index(op.f('ix_album_release_date'), 'album', ['release_date'], unique=False)
    op.create_table('genre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('song',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.Column('length', sa.String(length=25), nullable=True),
    sa.Column('release_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_song_name'), 'song', ['name'], unique=True)
    op.create_index(op.f('ix_song_release_date'), 'song', ['release_date'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(length=50), nullable=True),
    sa.Column('username', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('bio', sa.String(length=1000), nullable=True),
    sa.Column('pw_hash', sa.String(length=128), nullable=True),
    sa.Column('display_name', sa.String(length=100), nullable=True),
    sa.Column('join_date', sa.DateTime(), nullable=True),
    sa.Column('profile_public', sa.Boolean(), nullable=True),
    sa.Column('following_public', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_user_display_name'), 'user', ['display_name'], unique=False)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('artist',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('location', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artist_location'), 'artist', ['location'], unique=False)
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    op.create_table('listener',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('listener_to_genre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('listener_id', sa.Integer(), nullable=False),
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.Column('page_visit_count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['genre_id'], ['genre.id'], ),
    sa.ForeignKeyConstraint(['listener_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('poster_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=200), nullable=True),
    sa.Column('text', sa.String(length=1000), nullable=True),
    sa.Column('time_posted', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['poster_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_post_text'), 'post', ['text'], unique=False)
    op.create_index(op.f('ix_post_time_posted'), 'post', ['time_posted'], unique=False)
    op.create_index(op.f('ix_post_title'), 'post', ['title'], unique=False)
    op.create_table('request',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('subject', sa.String(length=144), nullable=True),
    sa.Column('description', sa.String(length=2056), nullable=True),
    sa.Column('category', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_request_category'), 'request', ['category'], unique=True)
    op.create_index(op.f('ix_request_description'), 'request', ['description'], unique=True)
    op.create_index(op.f('ix_request_subject'), 'request', ['subject'], unique=True)
    op.create_table('song_to_album',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('song_id', sa.Integer(), nullable=False),
    sa.Column('album_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['album_id'], ['album.id'], ),
    sa.ForeignKeyConstraint(['song_id'], ['song.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('artist_genre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], ),
    sa.ForeignKeyConstraint(['genre_id'], ['genre.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('artist_to_album',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('album_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['album_id'], ['album.id'], ),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('artist_to_listener',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('listener_id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('page_visit_count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], ),
    sa.ForeignKeyConstraint(['listener_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('artist_to_song',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('song_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], ),
    sa.ForeignKeyConstraint(['song_id'], ['song.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('poster_id', sa.Integer(), nullable=True),
    sa.Column('text', sa.String(length=1000), nullable=True),
    sa.Column('time_posted', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
    sa.ForeignKeyConstraint(['poster_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comment_text'), 'comment', ['text'], unique=False)
    op.create_index(op.f('ix_comment_time_posted'), 'comment', ['time_posted'], unique=False)
    op.create_table('similar_artists',
    sa.Column('referenced_artist_id', sa.Integer(), nullable=True),
    sa.Column('similar_artist_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['referenced_artist_id'], ['artist.id'], ),
    sa.ForeignKeyConstraint(['similar_artist_id'], ['artist.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('similar_artists')
    op.drop_index(op.f('ix_comment_time_posted'), table_name='comment')
    op.drop_index(op.f('ix_comment_text'), table_name='comment')
    op.drop_table('comment')
    op.drop_table('artist_to_song')
    op.drop_table('artist_to_listener')
    op.drop_table('artist_to_album')
    op.drop_table('artist_genre')
    op.drop_table('song_to_album')
    op.drop_index(op.f('ix_request_subject'), table_name='request')
    op.drop_index(op.f('ix_request_description'), table_name='request')
    op.drop_index(op.f('ix_request_category'), table_name='request')
    op.drop_table('request')
    op.drop_index(op.f('ix_post_title'), table_name='post')
    op.drop_index(op.f('ix_post_time_posted'), table_name='post')
    op.drop_index(op.f('ix_post_text'), table_name='post')
    op.drop_table('post')
    op.drop_table('listener_to_genre')
    op.drop_table('listener')
    op.drop_table('followers')
    op.drop_index(op.f('ix_artist_location'), table_name='artist')
    op.drop_table('artist')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_display_name'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_song_release_date'), table_name='song')
    op.drop_index(op.f('ix_song_name'), table_name='song')
    op.drop_table('song')
    op.drop_table('genre')
    op.drop_index(op.f('ix_album_release_date'), table_name='album')
    op.drop_index(op.f('ix_album_name'), table_name='album')
    op.drop_index(op.f('ix_album_description'), table_name='album')
    op.drop_table('album')
    # ### end Alembic commands ###
