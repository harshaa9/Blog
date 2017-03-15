import os
import unittest
from config import basedir
from app import app, db
from app.models import User, Post
from datetime import datetime, timedelta

class TestUniqueUser(unittest.TestCase):
  def setUp(self):
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] =False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + 'root' + ':' + 'bhava' + '@' + 'localhost' + "/" + 'EmpData'
    self.app = app.test_client()
    db.create_all()
    
  def teardown(self):
    db.session.remove()
    db.drop_all()
    
  def test_avatar(self):
    u = User(nickname = 'manohar', email = 'manohar@email.com', social_id = 'manohar')
    avatar = u.avatar(128)
    expected = 'http://www.gravatar.com/avatar/some id'
    assert avatar[0:len(expected)] == expected
    
  def test_make_unique_nickname(self):
    u1 = User(nickname = 'manohar', email = 'manohar@email.com', social_id = 'manohar')
    db.session.add(u1)
    db.session.commit()
    nickname = User.make_unique_nickname('manohar')
    assert nickname != 'manohar'
    u2 = User(nickname=nickname, email = "manohar1@email.com", social_id = 'manohar1')
    db.session.add(u2)
    db.session.commit()
    nickname2 = User.make_unique_nickname('manohar')
    assert nickname2 != 'manohar'
    assert nickname2 != nickname
    db.session.delete(u1)
    db.session.delete(u2)
    db.session.commit()

  def test_follow(self):
    u1 = User(nickname = 'mano', email = 'mano@email.com', social_id = 'mano')
    u2 = User(nickname = 'bhava', email = 'bhava@email.com', social_id = 'bhava')
    db.session.add(u1)
    db.session.add(u2)
    db.session.commit()
    assert u1.unfollow(u2) is None
    u = u1.follow(u2)
    db.session.add(u)
    db.session.commit()
    assert u1.follow(u2) is None
    assert u1.is_following(u2)
    assert u1.followed.count() == 1
    assert u1.followed.first().nickname == 'bhava'
    assert u2.followers.count() == 1
    assert u2.followers.first().nickname == 'mano'
    u = u1.unfollow(u2)
    assert u is not None
    db.session.add(u)
    db.session.commit()
    assert not u1.is_following(u2)
    assert u1.followed.count() == 0
    assert u2.followers.count() == 0
    db.session.delete(u1)
    db.session.delete(u2)
    db.session.commit()
  
  def test_follow_posts(self):
    # make users first
    u1 = User(nickname = 'mano', email = 'mano@email.com', social_id = 'mano')
    u2 = User(nickname = 'bhava', email = 'bhava@email.com', social_id = 'bhava')
    u3 = User(nickname = 'mary', email = 'mary@email.com', social_id = 'mary')
    u4 = User(nickname = 'david', email = 'david@email.com', social_id = 'david')
    db.session.add(u1)
    db.session.add(u2)
    db.session.add(u3)
    db.session.add(u4)
    # make four posts
    utcnow = datetime.utcnow()
    p1 = Post(body="post from mano", author=u1, timestamp=utcnow + timedelta(seconds=1))
    p2 = Post(body="post from bhava", author=u2, timestamp=utcnow + timedelta(seconds=2))
    p3 = Post(body="post from mary", author=u3, timestamp=utcnow + timedelta(seconds=3))
    p4 = Post(body="post from david", author=u4, timestamp=utcnow + timedelta(seconds=4))
    db.session.add(p1)
    db.session.add(p2)
    db.session.add(p3)
    db.session.add(p4)
    db.session.commit()
    # setup the followers
    u1.follow(u1)  # mano follows himself
    u1.follow(u2)  # mano follows bhava
    u1.follow(u4)  # mano follows david
    u2.follow(u2)  # bhava follows himself
    u2.follow(u3)  # bhava follows mary
    u3.follow(u3)  # mary follows herself
    u3.follow(u4)  # mary follows david
    u4.follow(u4)  # david follows himself
    db.session.add(u1)
    db.session.add(u2)
    db.session.add(u3)
    db.session.add(u4)
    db.session.commit()
    # check the followed posts of each user
    f1 = u1.followed_posts().all()
    f2 = u2.followed_posts().all()
    f3 = u3.followed_posts().all()
    f4 = u4.followed_posts().all()
    assert len(f1) == 3
    assert len(f2) == 2
    assert len(f3) == 2
    assert len(f4) == 1
    assert f1 == [p4, p2, p1]
    assert f2 == [p3, p2]
    assert f3 == [p4, p3]
    assert f4 == [p4]
    u1.unfollow(u1)  # mano follows himself
    u1.unfollow(u2)  # mano follows bhava
    u1.unfollow(u4)  # mano follows david
    u2.unfollow(u2)  # bhava follows himself
    u2.unfollow(u3)  # bhava follows mary
    u3.unfollow(u3)  # mary follows herself
    u3.unfollow(u4)  # mary follows david
    u4.unfollow(u4)
    db.session.delete(u1)
    db.session.delete(u2)
    db.session.delete(u3)
    db.session.delete(u4)
    db.session.delete(p1)
    db.session.delete(p2)
    db.session.delete(p3)
    db.session.delete(p4)
    db.session.commit()
    
if __name__ == '__main__':
  unittest.main()