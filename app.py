from flask import Flask, render_template, flash, redirect, url_for, session, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, LoginManager, UserMixin
from models import User, db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from config import conn_str
from sqlalchemy.orm import load_only
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import CSRFProtect
from flask_seasurf import SeaSurf


app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = conn_str
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False

csrf = CSRFProtect(app)

# Initialize the database
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import routes
from routes import *

if __name__ == '__main__':
    app.run(debug=True)

