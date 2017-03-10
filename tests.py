import os
import unittest
from config import basedir
from app import app, db
from app.models import User

class TestCase(unittest.TestCase):
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
    u = User(nickname='bhavandla', email = 'bhavandla@email.com')
    avatar = u.avatar(128)
    expected = 'http://www.gravatar.com/avatar/some id'
    assert avatar[0:len(expected)] == expected
    
  def test_make_unique_nickname(self):
    u = User(nickname="bhavandla", email = "bhavandla@email.com")
    db.session.add(u)
    db.session.commit()
    nickname = User.make_unique_nickname('bhavandla')
    assert nickname != 'bhavandla'
    u = User(nickname=nickname, email = "bsm@example.com")
    db.session.add(u)
    db.session.commit()
    nickname2 = User.make_unique_nickname('bhavandla')
    assert nickname2 != 'bhavandla'
    assert nickname2 != nickname
    
if __name__ == '__main__':
  unittest.main()