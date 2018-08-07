from wtforms import StringField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm

class LoginForm(FlaskForm):
    openid = StringField('openid', validators=[DataRequired()])
    remeber_me = BooleanField('remember_me', default=False)
    submit = SubmitField('Sign In')

class EditForm(FlaskForm):
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')