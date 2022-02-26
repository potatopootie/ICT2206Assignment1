from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError


app = Flask(__name__)
# creates database instance 
db = SQLAlchemy(app)
# to connect to database file 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'

# Table creation 
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

# Inherit from flask form (register)
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(),Length(min=4, max=20)], render_kw={"placeholder":"Username"})
    # Will be black dots for password input using PasswordField
    password = PasswordField(validators=[InputRequired(),Length(min=4, max=20)], render_kw={"placeholder":"Password"})
    submit = SubmitField("Register")

# Username validation 
def validate_username(self, username):
    existing_user_username = User.query.filter_by(
        username=username.data).first()
    # Username validation error if username already exists. 
    if existing_user_username:
        raise ValidationError(
            "That username already exists. Please choose a different one.")

# Inherit from flask form (login)
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(),Length(min=4, max=20)], render_kw={"placeholder":"Username"})
    # Will be black dots for password input using PasswordField
    password = PasswordField(validators=[InputRequired(),Length(min=4, max=20)], render_kw={"placeholder":"Password"})
    submit = SubmitField("Register")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)


