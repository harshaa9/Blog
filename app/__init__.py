from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flaskext.mysql import MySQL
from flask_login import LoginManager
from flask_mail import Mail
from .momentjs import momentjs
from flask_babel import Babel
from flask.json import JSONEncoder

app = Flask(__name__)
app.config.from_object('config')
mysql = MySQL()
mysql.init_app(app)
db = SQLAlchemy(app)

lm = LoginManager(app)

mail = Mail(app)

babel = Babel(app)

# from app import mail
# mail.mail_send_to_file()

app.jinja_env.globals['momentjs'] = momentjs

class CustomJSONEncoder(JSONEncoder):
  """This class adds support for lazy translation texts to flask's JSON encoder. This is neccessary when flashing translated texts."""
  def defualt(self, obj):
    from speaklater import is_lazy_string
    if is_lazy_string(obj):
      try:
        return unicode(obj)    # python 2
      except NameError:
        return str(obj)      # python 3
    return super(CustomJSONEncoder, self).defualt(obj)

app.json_encoder = CustomJSONEncoder

from app import views, models