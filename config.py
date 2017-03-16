WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

OPENID_PROVIDERS = [
    {'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id'},
    {'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
    {'name': 'AOL', 'url': 'http://openid.aol.com/<username>'},
    {'name': 'Flickr', 'url': 'http://www.flickr.com/<username>'},
    {'name': 'MyOpenID', 'url': 'https://www.myopenid.com'}]

import os
basedir = os.path.abspath(os.path.dirname(__file__))
MYSQL_DATABASE_USER= "root"
MYSQL_DATABASE_PASSWORD= "bhava"
MYSQL_DATABASE_DB= "EmpData"
MYSQL_DATABASE_HOST= "localhost"
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + MYSQL_DATABASE_USER + ':' + MYSQL_DATABASE_PASSWORD + '@' + MYSQL_DATABASE_HOST + "/" + MYSQL_DATABASE_DB
SQLALCHEMY_MIGRATE_REPO = os.path.join(SQLALCHEMY_DATABASE_URI, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True

OAUTH_CREDENTIALS = {
  'twitter': {
        'id': 'KVtUxq7sam44zgUbmLDz34IQo',
        'secret': 'ajLDgAbHDDzflfMjSnTmlJ2qzkapDs82srvDXO7yy2JFN3mMjj'
    },
  'facebook': {
        'id': '470154729788964',
        'secret': '010cc08bd4f51e34f3f3e684fbdea8a7'
    }
}

# # mail server settings
MAIL_SERVER = 'localhost'#'smtp.gmail.com'
MAIL_PORT = 9999 #465
MAIL_USE_TLS = False
MAIL_USE_SSL = False # use SSL unless its dev

MAIL_USERNAME = None
MAIL_PASSWORD = None
# MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
# MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

#administrator list
ADMINS = ['no-reply@microblog.com']



POSTS_PER_PAGE = 2

WHOOSH_BASE = os.path.join(basedir, 'search.sql')
MAX_SEARCH_RESULTS = 50