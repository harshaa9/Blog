from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flaskext.mysql import MySQL
from flask_login import LoginManager
from flask_mail import Mail
from .momentjs import momentjs

app = Flask(__name__)
app.config.from_object('config')
mysql = MySQL()
mysql.init_app(app)
db = SQLAlchemy(app)

lm = LoginManager(app)

mail = Mail(app)

# from app import mail
# mail.mail_send_to_file()

app.jinja_env.globals['momentjs'] = momentjs

from app import views, models