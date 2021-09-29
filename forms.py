from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import InputRequired, EqualTo, Length

class RegistrationForm(FlaskForm):
    user_id = StringField("User ID:",validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password:",validators=[InputRequired(), Length(min=4)])
    password2 = PasswordField("Confirm Password:",validators=[InputRequired(), EqualTo("password")])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    user_id = StringField("User ID:",validators=[InputRequired()])
    password = PasswordField("Password:",validators=[InputRequired()])
    submit = SubmitField("Submit")  

class SuggestionForm(FlaskForm):
    suggest = StringField("Enter your suggestion here: ",validators=[InputRequired(), Length(max=50)])
    true = StringField("Enter the true answer to your question: ",validators=[InputRequired(), Length(max=29)])
    falseA = StringField("Enter a false answer: ",validators=[InputRequired(), Length(max=29)])
    falseB = StringField("Enter another false answer: ",validators=[InputRequired(), Length(max=29)])
    falseC = StringField("Enter one more false answer: ",validators=[InputRequired(), Length(max=29)])
    submit = SubmitField("Submit")     

class DeleteForm(FlaskForm):
    quest_id = IntegerField("Quest ID of question you wish to delete: ", validators=[InputRequired()])
    submit = SubmitField("Submit")    