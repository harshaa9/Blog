import os
import unittest
from config import basedir
from app import app, db
from app.models import User

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

class TestFollow(unittest.TestCase):
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
    
if __name__ == '__main__':
  unittest.main()