from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired


class LoginForm(FlaskForm):
    username = StringField('Account Number', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class Register(FlaskForm):
    fname = StringField('First Name', validators=[InputRequired()])
    lname = StringField('Last Name', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])