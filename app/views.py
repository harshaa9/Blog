from flask import render_template, flash, redirect, url_for, request, g
from app import app, mysql, lm, db
from .forms import LoginForm, EditForm#, Email_change
from flaskext.mysql import MySQL
from oauth import OAuthSignIn
from flask_login import login_user, logout_user, current_user
from models import User
from flask_security import login_required
from datetime import datetime

lm.login_view = 'index'

@app.before_request
def before_request():
  user = current_user
  if user.is_authenticated:
    user.last_seen = datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    
def after_login(resp):
  user = current_user
  if user is None:
    nickname = resp.nickname
    flash("nickname found !")
    if nickname is None or nickname == '':
      nickname = resp.email.split('@')[0]
    nickname = User.make_unique_nickname(nickname)
    user = User(nickname = nickname, email = resp.email)
    flash("nickname added !")
    db.session.add(user)
    db.session.commit()

@app.route('/')
@app.route('/index')
def index():
  if current_user:
    user = current_user # fake user
  else:
    user = None
  posts = [  # fake array of posts
        { 
            'author': {'nickname': 'John'}, 
            'body': 'Beautiful day in Portland!' 
        },
        { 
            'author': {'nickname': 'Susan'}, 
            'body': 'The Avengers movie was so cool!' 
        }
    ]
  return render_template('index.html',title='Home', user=user, posts=posts)

@app.route('/user/<nickname>')
@login_required
def user(nickname):
  if nickname == current_user.nickname:
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
      flash('User %s not found.' % nickname)
      return redirect(url_for('index'))
    posts = [
      {'author': user, 'body': 'Test post #1'},
      {'author': user, 'body': 'Test post #2'}
    ]
    flash('User %s login successful.' % nickname)
    return render_template('user.html',user=user,posts=posts)
  else:
    flash("Your request can't process !. as you cant see other accounts details.!!!")
    return redirect(url_for('index'))

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         flash('Login requested for OpenID="%s", remember_me=%s' %
#               (form.openid.data, str(form.remember_me.data)), 'success')
#         return redirect(url_for('index'))
#     return render_template('login.html', 
#                            title='Sign In',
#                            form=form,
#                            providers=app.config['OPENID_PROVIDERS'])
  
@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('index'))

@app.route('/edit', methods = ['GET', 'POST'])
@login_required
def edit():
  user = current_user
  form = EditForm(user.nickname, user.email)
  if form.validate_on_submit():
    user.nickname = form.nickname.data
    user.about_me = form.about_me.data
    user.email = form.email.data
    db.session.add(user)
    db.session.commit()
    flash('Your changes have been saved.')
    return redirect(url_for('edit'))
  elif request.method != "POST":
    form.nickname.data = user.nickname
    form.about_me.data = user.about_me
    form.email.data = user.email
  return render_template('edit.html', form = form, user = user)
    
# @app.route("/Authenticate")
# def Authenticate():
#     username = request.args.get('UserName')
#     password = request.args.get('Password')
#     cursor = mysql.connect().cursor()
#     cursor.execute("SELECT * from User where Username='" + username + "' and Password='" + password + "'")
#     data = cursor.fetchone()
#     if data is None:
#      return "Username or Password is wrong"
#     else:
#      return "Logged in successfully"
  
@app.route('/authorize/<provider>')
def oauth_authorize(provider):
  if not current_user.is_anonymous:
    return redirect(url_for('index'))
  oauth = OAuthSignIn.get_provider(provider)
  return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    after_login(user)
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html', user = current_user), 500