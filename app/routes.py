import os
import fnmatch
from app import app
from time import strftime
from random import randint
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from flask import Flask, render_template, abort, flash, request, redirect, url_for
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, PasswordField, BooleanField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Newsticker, CoachingClass
from werkzeug.urls import url_parse
from app import db
from werkzeug import secure_filename

  
 
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
    #usertype = SelectField('User Type', choices = [('Student'), ('Coaching Class')])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    usertype = SelectField('User Type', choices = [('Admin', 'Admin'), ('Coaching', 'Coaching')], validators=[DataRequired()])
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

class UpdateNewsForm(FlaskForm):
    news = StringField('News', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CoachingRegistrationForm(FlaskForm):
    coachingname = StringField('coachingname', validators=[DataRequired()])
    coachingcontact = StringField('Contact', validators=[DataRequired()])
    coachingemail = StringField('Email', validators=[DataRequired(), Email()])
    coachingabout = StringField('About', validators=[DataRequired()])
    coachingcoursesoffered = StringField('Courses Offered', validators=[DataRequired()])
    coachingteachers = StringField('Teachers', validators=[DataRequired()])
    coachingachievement = StringField('Achievement', validators=[DataRequired()])
    coachingresults = StringField('Results', validators=[DataRequired()])
    coachingcategory = SelectField('Category', choices = [('Academic', 'Academic'), ('Entrance', 'Entrance'), ('Competition', 'Competition')], validators=[DataRequired()])
    coachingsubcategory = SelectField('Sub Category', choices = [('IIT', 'IIT'), ('UPSC', 'UPSC'), ('Bank', 'Bank'), ('12th', '12th')], validators=[DataRequired()])
    coachinglocation = SelectField('Location', choices = [('Patna', 'Patna'), ('Pune', 'Pune'), ('Mumbai', 'Mumbai'), ('Bokaro', 'Bokaro')], validators=[DataRequired()])
    submit = SubmitField('Register')

class EditNewsForm(FlaskForm):
    news = StringField('News', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

class EditCoachingForm(FlaskForm):
    coachingname = StringField('coachingname', validators=[DataRequired()])
    coachingcontact = StringField('Contact', validators=[DataRequired()])
    coachingemail = StringField('Email', validators=[DataRequired(), Email()])
    coachingabout = StringField('About', validators=[DataRequired()])
    coachingcoursesoffered = StringField('Courses Offered', validators=[DataRequired()])
    coachingteachers = StringField('Teachers', validators=[DataRequired()])
    coachingachievement = StringField('Achievement', validators=[DataRequired()])
    coachingresults = StringField('Results', validators=[DataRequired()])
    coachingcategory = SelectField('Category', choices = [('Academic', 'Academic'), ('Entrance', 'Entrance'), ('Competition', 'Competition')], validators=[DataRequired()])
    coachingsubcategory = SelectField('Sub Category', choices = [('IIT', 'IIT'), ('UPSC', 'UPSC'), ('Bank', 'Bank'), ('12th', '12th')], validators=[DataRequired()])
    coachinglocation = SelectField('Location', choices = [('Patna', 'Patna'), ('Pune', 'Pune'), ('Mumbai', 'Mumbai'), ('Bokaro', 'Bokaro')], validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/')
@app.route('/home')
def home():
    news = Newsticker.query.all()
    files = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/home")), '*.jpg')
    return render_template('home.html', items=ITEMS, news=news, files=files)
 
@app.route('/item/<key>')
def item(key):
    #item = productsList.get(key)
    item = CoachingClass.query.get(key)
    CoachingClassSliderimages = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(item.coachingid) + '_' + '*' + '_' +'CoachingClassSliderfile*' + '_' + '*.jpg')
    CoachingClassAchievementimages = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(item.coachingid) + '_' + '*' + '_' +'CoachingClassAchievementfile' + '_' + '*.jpg')
    CoachingClassResultsimages = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(item.coachingid) + '_' + '*' + '_' +'CoachingClassResultsfile' + '_' + '*.jpg')
    if not item:
        abort(404)
    return render_template('item.html', item=item, CoachingClassSliderimages=CoachingClassSliderimages, CoachingClassAchievementimages=CoachingClassAchievementimages, CoachingClassResultsimages=CoachingClassResultsimages)

@app.route('/productList')
def productList():
    productsList = CoachingClass.query.all()
    return render_template('productList.html', productList=productsList)

@app.route("/coachingregistration", methods=['GET', 'POST'])
def coachingregistration():
    print(request.form.get('submit'))
    if request.form.get('submit') == 'submit_images':
        print(request.form.get('submit'))
        coaching_id = current_user.coachingclass.all()[0].coachingid
        filefield = ['CoachingClassSliderfile1', 'CoachingClassSliderfile2', 'CoachingClassSliderfile3', 'CoachingClassSliderfile4', 'CoachingClassSliderfile5', 'CoachingClassAchievementfile', 'CoachingClassResultsfile']
        for file in filefield:
            f = request.files[file]
            f.filename = str(coaching_id) + "_" + str(filefield.index(file)) + "_" + file + "_" + f.filename
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_COACHING_FOLDER'], filename))
        return redirect(url_for('home'))
    else:
        form = CoachingRegistrationForm()
        if form.validate_on_submit():
            regCoaching = CoachingClass(coachingname=form.coachingname.data, coachingcontact=form.coachingcontact.data, coachingemail=form.coachingemail.data, coachingpassword_hash='sjkfjlsdjflasdfjkldjflksdfjksdjlfsd', coachingabout=form.coachingabout.data, coachingcoursesoffered=form.coachingcoursesoffered.data, coachingteachers=form.coachingteachers.data, coachingachievement=form.coachingachievement.data, coachingresults=form.coachingresults.data, coachingcategory=form.coachingcategory.data, coachingsubcategory=form.coachingsubcategory.data, coachinglocation=form.coachinglocation.data, author=current_user)
            db.session.add(regCoaching)
            db.session.commit()
            return redirect(url_for('productList'))
    return render_template('coachingregistration.html', title='Register Coaching', form=form)


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
            next_page = url_for('home')
        return redirect(next_page)
#        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/StudentDescrition')
def StudentDescrition():
    # ...
    return render_template("StudentDescrition.html", title='Home Page', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        print(form.usertype.data)
        #if form.usertype.data == 'Coaching':
        user = User(username=form.username.data, email=form.email.data, usertype=form.usertype.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/contactUs')
def contactUs():
    return render_template('contactUs.html')

@app.route("/updateNewsFeed", methods=['GET', 'POST'])
def updateNewsFeed():
    currentNews = Newsticker.query.all()
    form = UpdateNewsForm()
    if form.validate_on_submit():
        print(form.news.data)
        newNews = Newsticker(news=form.news.data)
        db.session.add(newNews)
        db.session.commit()
        flash('Congratulations, News live now!')
        return redirect(url_for('updateNewsFeed'))
    return render_template('updateNewsFeed.html', title='Update News', form=form, currentNews=currentNews)

@app.route('/mycoaching/<key>')
def mycoaching(key):
    #item = productsList.get(key)
    mycoaching = CoachingClass.query.get(key)
    #images = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(item.coachingid) + '_' + '*.jpg')
    if not mycoaching:
        abort(404)
    return render_template('mycoaching.html', mycoaching=mycoaching)

@app.route('/edit_news/<key>', methods=['GET', 'POST'])
def edit_news(key):
    form = EditNewsForm()
    if form.validate_on_submit():
        News = Newsticker.query.get(key)
        News.news = form.news.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('updateNewsFeed'))
    elif request.method == 'GET':
        News = Newsticker.query.get(key)
        form.news.data = News.news
    return render_template('edit_news.html', title='Edit News',
                           form=form)

@app.route('/edit_coaching/<key>', methods=['GET', 'POST'])
def edit_coaching(key):
    form = EditCoachingForm()
    mycoaching = CoachingClass.query.get(key)
    coaching_id = current_user.coachingclass.all()[0].coachingid
    coachingSlideImg_list = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(coaching_id) + '_' + '*' + '_' + 'CoachingClassSliderfile*' + '*.jpg')
    coachingAchievementImg_list = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(coaching_id) + '_' + '*' + '_' + 'CoachingClassAchievementfile*' + '*.jpg')
    coachingResultsImg_list = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(coaching_id) + '_' + '*' + '_' + 'CoachingClassResultsfile*' + '*.jpg')
    print("hi1")
    print(coachingSlideImg_list)
    print("hi2")
    if form.validate_on_submit():
        Coaching = CoachingClass.query.get(key)
        Coaching.coachingname = form.coachingname.data
        Coaching.coachingcontact = form.coachingcontact.data
        Coaching.coachingemail = form.coachingemail.data
        Coaching.coachingabout = form.coachingabout.data
        Coaching.coachingcoursesoffered = form.coachingcoursesoffered.data
        Coaching.coachingteachers = form.coachingteachers.data
        Coaching.coachingachievement = form.coachingachievement.data
        Coaching.coachingresults = form.coachingresults.data 
        Coaching.coachingcategory = form.coachingcategory.data 
        Coaching.coachingsubcategory = form.coachingsubcategory.data
        Coaching.coachinglocation = form.coachinglocation.data 
        db.session.commit()
        flash('Your changes have been saved.')
        return render_template('mycoaching.html', mycoaching=mycoaching)
    elif request.method == 'GET':
        Coaching = CoachingClass.query.get(key)
        form.coachingname.data = Coaching.coachingname
        form.coachingcontact.data = Coaching.coachingcontact
        form.coachingemail.data = Coaching.coachingemail
        form.coachingabout.data = Coaching.coachingabout
        form.coachingcoursesoffered.data = Coaching.coachingcoursesoffered
        form.coachingteachers.data = Coaching.coachingteachers
        form.coachingachievement.data = Coaching.coachingachievement
        form.coachingresults.data = Coaching.coachingresults
        form.coachingcategory.data = Coaching.coachingcategory
        form.coachingsubcategory.data = Coaching.coachingsubcategory
        form.coachinglocation.data = Coaching.coachinglocation
    return render_template('edit_coaching.html', title='Edit Coaching',
                           form=form, coachingSlideImg_list=coachingSlideImg_list, coachingAchievementImg_list=coachingAchievementImg_list, coachingResultsImg_list=coachingResultsImg_list)

@app.route('/uploadHomeImages', methods = ['GET', 'POST'])
def uploadHomeImages():
   if request.method == 'POST':
      f = request.files['file']
      filename = secure_filename(f.filename)
      f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      return redirect(url_for('home'))
   return render_template('uploadHomeImages.html')
	
@app.route('/manageHomeImages')
def manageHomeImages():
    #homeImg_list = os.listdir(app.config['UPLOAD_FOLDER'])
    homeImg_list = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/home")), '*.jpg')
    return render_template('manageHomeImages.html', homeImg_list=homeImg_list)		

@app.route('/deleteHomeImages/<filename>')
def deleteHomeImages(filename):
    file_name = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    os.remove(file_name)
    return redirect(url_for('manageHomeImages'))

@app.route('/uploadCoachingImages', methods = ['GET', 'POST'])
def uploadCoachingImages():
   if request.method == 'POST':
      coaching_id = current_user.coachingclass.all()[0].coachingid
      filefield = ['CoachingClassSliderfile1', 'CoachingClassSliderfile2', 'CoachingClassSliderfile3', 'CoachingClassSliderfile4', 'CoachingClassSliderfile5', 'CoachingClassAchievementfile', 'CoachingClassResultsfile']
      for file in filefield:
          f = request.files[file]
          f.filename = str(coaching_id) + "_" + str(filefield.index(file)) + "_" + file + "_" + f.filename
          filename = secure_filename(f.filename)
          f.save(os.path.join(app.config['UPLOAD_COACHING_FOLDER'], filename))
      return redirect(url_for('home'))
   return render_template('uploadCoachingImages.html')

#@app.route('/manageCoachingImages', methods = ['GET', 'POST'])
#def manageCoachingImages():
#    coaching_id = current_user.coachingclass.all()[0].coachingid
#    coachingSlideImg_list = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(item.coachingid) + '_' + '*' + '_' + 'CoachingClassSliderfile*' + '*.jpg')
#    coachingAchievementImg_list = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(item.coachingid) + '_' + '*' + '_' + 'CoachingClassAchievementfile*' + '*.jpg')
#    coachingResultsImg_list = fnmatch.filter(os.listdir(os.path.join(app.static_folder, "img/coaching_slide")), str(item.coachingid) + '_' + '*' + '_' + 'CoachingClassResultsfile*' + '*.jpg')
#    print("hi1")
#    print(coachingSlideImg_list)
#    print("hi2")
#    return render_template('edit_coaching.html', coachingSlideImg_list=coachingSlideImg_list, coachingAchievementImg_list=coachingAchievementImg_list, coachingResultsImg_list=coachingResultsImg_list)		

@app.route('/deleteCoachingImages/<filename>', methods = ['GET', 'POST'])
def deleteCoachingImages(filename):
    file_name = os.path.join(app.config['UPLOAD_COACHING_FOLDER'], filename)
    os.remove(file_name)
    return redirect(url_for('manageCoachingImages'))
