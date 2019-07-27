from app import app
from time import strftime
from random import randint
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from flask import Flask, render_template, abort, flash, request, redirect, url_for
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse
from app import db

  
 
ITEMS = {
    'coaching': {
        'name': 'Coaching Classes',
        'category': 'coaching',
        'price':'Starting at 1000',
    },
#    'hostels': {
#        'name': 'Hostels',
#        'category': 'Phones',
#        'price':'Starting at 1500',
#    },
#    'rooms': {
#        'name': 'Individual rooms/flats',
#        'category': 'Tablets',
#        'price':'Starting at 1500',
#    },
#    'examinee': {
#        'name': 'Examinee rooms',
#        'category': 'Tablets',
#        'price':'Starting at 2500'
#    }
}
 
productsList = {
    'coaching1': {
        'id': '100',
        'name': 'A Coaching Classes',
        'category': 'IIT',
	'location': 'Patna',
	'overview' : 'A Coaching Classes is leading coaching institute in Patna for IIT JEE exam. Best IIT JEE Coaching in Patna.',
        'price':'Starting at 1000',
    },  
    'coaching2': {
        'id': '101',
        'name': 'B Coaching Classes',
        'category': 'IIT',
        'location': 'Patna',
	'overview' : 'B Coaching Classes is leading coaching institute in Patna for IIT JEE exam. Best IIT JEE Coaching in Patna.',
        'price':'Starting at 1500',
    },
    'coaching3': {
        'id': '103',
        'name': 'C Coaching Classes',
        'category': 'GATE',
        'location': 'Mumbai',
	'overview' : 'C Coaching Classes is leading coaching institute in Mumbai for GATE exam.',
        'price':'Starting at 1600',
    },
    'coaching4': {
        'id': '104',
        'name': 'D Coaching Classes',
        'category': 'UPSC',
        'location': 'Pune',
	'overview' : 'D Coaching Classes is leading coaching institute in Pune for UPSC exam. Best UPSC Coaching in Pune.',
        'price':'Starting at 100',
    },
    'coaching5': {
        'id': '105',
        'name': 'E Coaching Classes',
        'category': 'UPSC',
        'location': 'Pune',
	'overview' : 'E Coaching Classes is leading coaching institute in Pune for UPSC exam.',
        'price':'Starting at 2500'
    }
}


class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])

def get_time():
    time = strftime("%Y-%m-%dT%H:%M")
    return time

def write_to_disk(name, email):
    data = open('file.log', 'a')
    timestamp = get_time()
    data.write('DateStamp={}, Name={}, Email={} \n'.format(timestamp, name, email))
    data.close()


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', items=ITEMS)
 
@app.route('/item/<key>')
def item(key):
    item = productsList.get(key)
    if not item:
        abort(404)
    return render_template('item.html', item=item)

@app.route('/productList')
def productList():
    return render_template('productList.html', productList=productsList)

@app.route("/CoachingInput", methods=['GET', 'POST'])
def CoachingInput ():
    form = ReusableForm(request.form)

    #print(form.errors)
    if request.method == 'POST':
        name=request.form['name']
        email=request.form['email']
        mobile=request.form['mobile']
        password=request.form['password']
        CoachingType=request.form['Coaching Type']

        if form.validate():
            write_to_disk(name, email)
            flash('Hello: {}'.format(name))

        else:
            flash('Error: All Fields are Required')

    return render_template('CoachingInput.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('CoachingInput'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('CoachingInput')
        return redirect(next_page)
#        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/StudentDescrition')
def StudentDescrition():
    # ...
    return render_template("StudentDescrition.html", title='Home Page', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
