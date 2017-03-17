from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Email
from models import User

class LoginForm(FlaskForm):
    openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class PostForm(FlaskForm):
  post = TextAreaField('post', validators = [DataRequired()] )

class SearchForm(FlaskForm):
  search = StringField('search', validators = [DataRequired()])
  
class EditForm(FlaskForm):
  nickname = StringField('nickname', validators = [DataRequired()])
  about_me = TextAreaField('about_me', validators = [Length(min=0, max=140)])
  email = StringField('email', validators = [
    DataRequired(), Email("Please enter proper email address!")])
  
  def __init__(self, original_nickname, original_email, *args, **kwargs):
    FlaskForm.__init__(self, *args, **kwargs)
    self.original_nickname = original_nickname
    self.original_email = original_email
    
  def validate(self):
    if not FlaskForm.validate(self):
      return False
    if self.nickname.data == self.original_nickname and self.email.data != None and self.original_email != None and self.email.data == self.original_email:
      return True
    if self.nickname.data != User.make_valid_nickname(nickname):
      self.nickname.errors.append(gettext('This nickname has invalid characters. Please use letter, numbers, dots and underscores only.'))
      return False
    user = User.query.filter_by(nickname = self.nickname.data).first()
    email = User.query.filter_by(email = self.email.data).first()
    if user != None:
      self.nickname.errors.append(gettext('This nickname is already in use. Please choose another name.'))
      self.nickname.errors.append(gettext("\n you can use these available nicknames! "))
      self.nickname.errors.append(User.make_unique_nickname(self.nickname.data))
    if email != None:
      self.email.errors.append(gettext("This email is already in use. Please choose another email."))
      return False
    return True
  
#   def validate_nickname(FlaskForm, field):
# #     if field.data == original_nickname:
# #       return True
#     user = User.query.filter_by(nickname = field.data).first()
#     if user != None:
#       field.errors.append('This nickname is already in use. Please choose another name.')
#       field.errors.append("\n you can use these available nicknames! ")
#       field.errors.append(User.make_unique_nickname(field.data))
#     return True
    
  
#   def validate_email(FlaskForm, field):
# #     if fiel.ddata != None and original_email != None and field.data == original_email:
# #       return True
#     email = User.query.filter_by(email = field.data).first()
#     if email != None:
#       field.errors.append("This email is already in use. Please choose another email.'")
#     return True
      
    