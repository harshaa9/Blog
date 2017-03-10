from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flaskext.mysql import MySQL
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object('config')
mysql = MySQL()
mysql.init_app(app)
db = SQLAlchemy(app)

lm = LoginManager(app)

from app import mail
mail.mail_send_to_file()

from app import views, models