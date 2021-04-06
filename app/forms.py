from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired
from wtforms.fields.simple import BooleanField, SubmitField, TextAreaField
from wtforms.fields.core import FormField, IntegerField

class AllergyForm(FlaskForm):

    
    A_1 = BooleanField("Dairy")
    A_2 = BooleanField("Eggs")
    A_3 = BooleanField("Nuts")
    A_4 = BooleanField("Shellfish")
    A_5 = BooleanField("Soy")
    A_7 = BooleanField("Gluten")
    A_9= BooleanField("Seafood")

class LoginForm(FlaskForm):
    username = StringField('Account Number', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class Register(FlaskForm):
    fname = StringField('First Name', validators=[InputRequired()])
    lname = StringField('Last Name', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    allergies = FormField(AllergyForm)

class SearchForm(FlaskForm):
    search = StringField('Enter Recipe Title')
    submit = SubmitField("Search")

class RecipeForm(FlaskForm):
    title = StringField('Enter Recipe Title')
    cal = StringField('Calories')
    desc = TextAreaField('Description')
    prep  = IntegerField('Prep Time')
    submit = SubmitField("Add Recipe")

class InfoForm(FlaskForm):
    servings = IntegerField()

class MealPlanForm(FlaskForm):
    cal = IntegerField('Calories')