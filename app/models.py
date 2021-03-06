from app import app, db, lm
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from hashlib import md5
import re
import sys
if sys.version_info >= (3,0):
  enable_search = False
else:
  enable_search = True
  import flask_whooshalchemy as whooshalchemy

followers = db.Table('followers',
                    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
                    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
                    )

class User(UserMixin, db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  social_id = db.Column(db.String(64), nullable= False, unique=True)
  nickname = db.Column(db.String(64), nullable=False, unique=True)
  email = db.Column(db.String(64), nullable=True)
  posts = db.relationship('Post', backref='author', lazy='dynamic')
  about_me = db.Column(db.String(140))
  last_seen = db.Column(db.DateTime)
  followed = db.relationship('User',
                            secondary = followers,
                            primaryjoin = (followers.c.follower_id == id),
                            secondaryjoin = (followers.c.followed_id == id),
                            backref = db.backref('followers', lazy='dynamic'),
                            lazy = 'dynamic')
  
  @staticmethod
  def make_valid_nickname(nickname):
    return res.sub('[^a-zA-Z0-9_\.]', '', nickname)
  
  def avatar(self, size):
    if self.email:
      return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)
    return None
  
  def follow(self, user):
    if not self.is_following(user):
      self.followed.append(user)
      return self
    
  def unfollow(self, user):
    if self.is_following(user):
      self.followed.remove(user)
      return self
  
  def is_following(self, user):
    return self.followed.filter(followers.c.followed_id == user.id).count() > 0
  
  def followed_posts(self):
    return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())
  
  @staticmethod
  def make_unique_nickname(nickname):
    if User.query.filter_by(nickname=nickname).first() is None:
      return nickname
    version = 2
    while True:
      new_nickname = nickname + str(version)
      if User.query.filter_by(nickname = new_nickname).first() is None:
        break
      version += 1
    return new_nickname

@lm.user_loader
def load_user(id):
  return User.query.get(int(id))

"""class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % (self.nickname)
"""
class Post(db.Model):
  __searchable__ = ['body']
  
  id = db.Column(db.Integer, primary_key=True)
  body = db.Column(db.String(140))
  timestamp = db.Column(db.DateTime)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  
  def __repr__(self):
    return '<post %r>' % (self.body)

if enable_search:
  whooshalchemy.whoosh_index(app, Post)

  