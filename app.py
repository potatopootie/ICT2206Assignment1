from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required,  logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
import random
import subprocess

app = Flask(__name__)
# creates database instance 
db = SQLAlchemy(app)
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

# Inherit from flask form (login)
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(),Length(min=4, max=20)], render_kw={"placeholder":"Username"})
    # Will be black dots for password input using PasswordField
    password = PasswordField(validators=[InputRequired(),Length(min=4, max=20)], render_kw={"placeholder":"Password"})
    submit = SubmitField("Login")

# Register routing portion here 
@app.route('/register')
def register():
    N = 4
    images_ = random.sample(range(10, 26), N * N)
    images = []
    for i in range(0, N * N, N):
        images.append(images_[i:i + N])
    return render_template('register.html',images=images)

@app.route('/register', methods=['POST'])
def register_post():
    form = RegisterForm()
    username = request.form.get('username')
    if(request.form.get('row') and request.form.get('column')):
        row = request.form.get('row')
        col = request.form.get('column')
        password = row+col
        print(password, ".....")
    else:
        password_1 = sorted(request.form.getlist('password'))
        password_1 = ''.join(map(str, password_1))
        if len(password_1) < 6:
            flash("password must be minimum 3 selections")
            return redirect(url_for('register'))
        else:
            password = password_1
    user = User.query.filter_by(username=username).first()
    # Username validation error if username already exists. 
    if user:
        raise ValidationError(
            "That username already exists. Please choose a different one.")
    
    new_user = User(username=form.username.data, password=generate_password_hash(password, method='sha256'))
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('login'))

@app.route('/login')
def login():
    N = 4
    images_ = random.sample(range(10, 26), N * N)
    images = []
    for i in range(0, N * N, N):
        images.append(images_[i:i + N])
    return render_template('login.html',images=images)

@app.route('/login', methods=['POST'])
def login_post():
    form = LoginForm()
    username = request.form.get('username')
    if(request.form.get('row-column')):
        password = request.form.get('row-column')
        print(password,".....")
    else:
        password_1= sorted(request.form.getlist('password'))
        password_1 =''.join(map(str, password_1))
        if len(password_1) < 2:
            flash("password must be minimum 3 selections")
            return redirect(url_for('login'))
        else:
            password = password_1

    user = User.query.filter_by(username=username).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('login'))  # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/password_register')
def choosePasswordRegister():
   result = subprocess.check_output("python gazetracking.py", shell=True)
   return render_template('register.html', **locals())

@app.route('/password_login')
def choosePasswordLogin():
   result = subprocess.check_output("python gazetracking.py", shell=True)
   return render_template('login.html', **locals())

if __name__ == '__main__':
    app.run(debug=True)
