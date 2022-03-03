from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required,  logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import random

app = Flask(__name__)
# creates database instance 
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
# to connect to database file 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'

# Allow app and flask to work together
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Used to reload user object from user id stored in session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    submit = SubmitField("Login")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # Checks if user credentials matches the ones in the database
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    N = 6
    images_ = random.sample(range(10, 46), N * N)
    images = []
    for i in range(0, N * N, N):
        images.append(images_[i:i + N])
    if form.validate_on_submit():
        # whenever form is submitted, hashed password will immediately be generate 
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html',images=images)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)


