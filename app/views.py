from flask import render_template, flash, redirect, url_for, request, g, session
from app import app, mysql, lm, db
from .forms import LoginForm, EditForm, PostForm, SearchForm#, Email_change
from flaskext.mysql import MySQL
from oauth import OAuthSignIn
from flask_login import login_user, logout_user, current_user
from models import User, Post
from flask_security import login_required
from datetime import datetime
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS
from .emails import follower_notification

lm.login_view = 'index'

@lm.unauthorized_handler
def unauthorized():
  flash("Please login into your account first: ")
  return redirect(url_for('index'))

@app.before_request
def before_request():
  g.user = current_user
  if g.user.is_authenticated:
    user.last_seen = datetime.utcnow()
    db.session.add(g.user)
    db.session.commit()
    g.search_form = SearchForm()

@app.route('/search', methods = ['POST'])
@login_required
def search():
  if not g.search_form.validate_on_submit():
    return redirect(url_for('index'))
  return redirect(url_for('search_results', query = g.search_form.search.data))

@app.route('/search_results/<query>')
@login_required
def search_results(query):
  results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
  return render_template('search_results.html', query= query, results=results)
    
def after_login(user):
  if user:
    nickname = user.nickname
    if nickname is None or nickname == '':
      nickname = resp.email.split('@')[0]
    if User.query.filter_by(nickname=nickname).first():
      flash("your default nickname from twitter is already exists:  " + nickname)
      nickname = User.make_unique_nickname(nickname)
    flash("Your new nickname is: " + nickname)
    flash("You can change your nickname name in settings!")
    return nickname

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods = ["GET", "POST"])
def index(page = 1):
  if current_user:
    user = current_user # fake user
  else:
    user = None
  form = PostForm()
  if form.validate_on_submit():
    post = Post(body=form.post.data, timestamp = datetime.utcnow(), author=user)
    db.session.add(post)
    db.session.commit()
    flash("You post is now live!")
    return redirect(url_for('index'))
  if not user.is_anonymous:
    posts = user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
  else:
    posts = None
  return render_template('index.html',title='Home', user=user, form = form, posts=posts, ret = 'index')

@app.route('/user/<nickname>', methods=['GET', 'POST'])
@app.route('/user/<nickname>/<int:page>', methods=['GET', 'POST'])
@login_required
def user(nickname, page = 1):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
      flash('User %s not found.' % nickname)
      return redirect(url_for('index'))
    posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html',user=user,posts=posts, ret = 'user')

@app.route('/users_list', methods=['GET', 'POST'])
@login_required 
def users_list():
  user = current_user;
  users_list = User.query.all()
  return render_template('users_list.html', user = user, users_list = users_list)
  
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

@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
  user = User.query.filter_by(nickname=nickname).first()
  if user is None:
    flash('user %s not found.' % nickname)
    return redirect(url_for('index'))
  if user == current_user:
    flash("you can\'t follow yourself!")
    return redirect(url_for('user', nickname = nickname))
  u = current_user.follow(user)
  if u is None:
    flash("Cannot follow " + nickname + '.')
    return redirect(url_for('user', nickname = nickname))
  db.session.add(u)
  db.session.commit()
  flash('You are now following ' + nickname)
  follower_notification(user, g.user)
  return redirect(url_for('user', nickname = nickname))

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
  user = User.query.filter_by(nickname = nickname).first()
  if user is None:
    flash('user %s not found.' % nickname)
    return redirect(url_for('index'))
  if user == current_user:
    flash("you can\'t unfollow yourself!")
    return redirect(url_for('user', nickname = nickname))
  u = current_user.unfollow(user)
  if u is None:
    flash("Cannot unfollow " + nickname + '.')
    return redirect(url_for('user', nickname = nickname))
  db.session.add(u)
  db.session.commit()
  flash('You have stopped following ' + nickname)
  return redirect(url_for('user', nickname = nickname))
  
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
        user.nickname = after_login(user)
        db.session.add(user)
        db.session.commit()
        db.session.add(user.follow(user))
        db.session.commit()
    remember_me = False
#     if 'remember_me' in session:
#       remember_me = session['remember_me']
#       session.pop('remember_me', None)
    login_user(user, True) #remember = remember_me)
    flash('User %s login successful.' % user.nickname)
    return redirect(request.args.get('next') or url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html', user = current_user), 500