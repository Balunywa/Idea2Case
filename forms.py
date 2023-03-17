
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class SubmitIdeaForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    problem = TextAreaField('Problem', validators=[DataRequired()])
    submit = SubmitField('Submit Idea')
